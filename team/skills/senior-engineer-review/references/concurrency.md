# Concurrency & IPC Reference

Concurrency bugs are the worst kind: they hide in dev, fire in production under load, and the stack trace is useless. The only defense is reviewing for them on purpose, with a checklist.

## Quick IPC review checklist (run first on any IPC code)

For any code involving fork, pipes, FIFOs, semaphores, message queues, shared memory, or signals — run this list before going deeper:

1. **Creation race**: when two processes race to create the IPC resource, is exactly one the creator and initializer? Look for `IPC_CREAT | IPC_EXCL` (or POSIX `O_EXCL`).
2. **Initialization atomicity**: between creating a semaphore and `SETVAL`-ing its initial value, can another process see it at 0 and proceed? Often yes — needs an explicit sync pattern.
3. **`SEM_UNDO` decision**: if a process dies while holding a semaphore, is the semaphore released? Without `SEM_UNDO` the system-wide state can deadlock.
4. **`EINTR` everywhere**: every blocking IPC call (`semop`, `msgsnd`, `msgrcv`, `read`, `write`) can return -1 with `errno == EINTR`. Either loop and retry, or set `SA_RESTART` on handlers. *Not optional.*
5. **Cleanup on exit**: does the code call `IPC_RMID` / `msgctl(..., IPC_RMID)` / `shmctl(..., IPC_RMID)` on normal and abnormal exit? Use `atexit` or a signal handler that sets a flag. Stale IPC accumulates and `ipcs` will show it after the run.
6. **Message type discipline (msgq)**: if using PID-as-mtype for client replies, are PIDs unique enough for the run's duration? On long-running systems PIDs cycle.
7. **Size limits**: messages capped at `MSGMAX`; queue capped at `MSGMNB`. `msgsnd` blocks (or returns `EAGAIN` with `IPC_NOWAIT`) on full queue.
8. **Pipe atomicity**: writes ≤ `PIPE_BUF` (typically 4096) are atomic across processes; larger writes can interleave. `SIGPIPE` kills writer when reader closes — handle or ignore explicitly.
9. **Fork hygiene**: after `fork`, both processes have every file descriptor. Close the ends you won't use in each. Reap zombies with `waitpid` or `SIGCHLD`+`SIG_IGN`.
10. **Signal safety**: anything inside a signal handler must be async-signal-safe. `printf` is not. Use the self-pipe trick.

## The two questions for every shared piece of state

1. **Who reads it, who writes it?** If more than one thread/process touches it and at least one writes, it needs synchronization.
2. **Is access atomic?** A *single* protected write or read is rarely enough — operations are usually compound (read-modify-write, check-then-act), and the whole sequence needs to be atomic.

## Race types

### Data races
Concurrent read and write of the same memory without synchronization. In C/C++/Go this is *undefined behavior* — the compiler can do anything, including miscompile your code. Use mutexes, atomics, or message passing.

### Race conditions (logical races, not data races)
The data accesses might each be atomic, but the *sequence* is wrong:
```c
if (account.balance >= amount) {     // check
    account.balance -= amount;        // act
}
```
Two callers can both pass the check before either decrements. Fix: hold the lock across check-and-act, or use a transaction, or use compare-and-swap.

### TOCTOU on the filesystem
```c
if (access(path, R_OK) == 0) {    // check
    fd = open(path, O_RDONLY);     // use — attacker may have swapped path
}
```
Fix: `open` directly with appropriate flags (`O_NOFOLLOW`, `O_CREAT | O_EXCL`), check the result.

### Memory visibility
Just because thread A wrote a value doesn't mean thread B will see it without a memory barrier or release/acquire ordering. In Java use `volatile` or `synchronized`; in Go use `sync/atomic` or a mutex; in C/C++ use `<atomic>` with the right ordering; in Rust the type system forces this on you.

## Deadlocks

Four conditions, all required (Coffman): mutual exclusion, hold-and-wait, no preemption, circular wait. Break any one to prevent.

Practical advice:
- **Lock ordering**: pick a total order over all locks in the program and *always* acquire in that order. Document it.
- **No nested locks**: if you can structure code so only one lock is held at a time, deadlock is impossible.
- **`try_lock` with backoff** for the cases you can't restructure.
- **Lock with timeout** and fail loudly: deadlock as panic is debuggable; deadlock as hang is not.

## Livelock and starvation

- **Livelock**: threads make progress but no useful work (mutual yielding). Less common but easy to hand-code accidentally.
- **Starvation**: one thread never gets the lock. Use fair locks (`ReentrantLock(true)` in Java) if you care; most don't, but reader-writer locks with writer starvation are a classic.

## Atomicity boundaries

Things that look atomic but aren't:
- `x++` in C/C++/Java: read, increment, write — three steps.
- `dict[k] += 1` in Python: GIL holds across each bytecode but *not* across this compound operation.
- "Read config, check version, reload" — three steps; another thread can swap config between them.
- `if not exists: insert` in SQL without `INSERT ... ON CONFLICT` or `SELECT ... FOR UPDATE` — classic race.

## Cancellation and shutdown

- Background tasks/goroutines/threads need a cancellation channel/token/flag. Otherwise: leaks on shutdown.
- Pending I/O: close the socket / cancel the context, don't just hope the goroutine notices.
- Cleanup order matters: drain queues before stopping workers, not after.

## Signal safety (POSIX C)

Inside a signal handler you may only call **async-signal-safe** functions. The list is short: `write`, `_exit`, `signal`, `kill`, `read`, a handful of others. Not safe: `printf`, `malloc`, `free`, anything that takes a non-reentrant lock.

The self-pipe trick is the canonical solution: handler writes one byte to a pipe; main loop reads it via `select`/`poll`/`epoll`. All real work happens outside the handler.

## IPC pitfalls (System V & POSIX)

### Pipes / FIFOs
- `SIGPIPE` when writing to a pipe whose reader closed. Either handle the signal, or `signal(SIGPIPE, SIG_IGN)` and check `EPIPE` from `write`.
- Writes ≤ `PIPE_BUF` (typically 4096) are atomic; larger writes can interleave between processes.
- Pipes inherited across `fork`: close them in the wrong end of each process, or they'll never EOF.

### System V semaphores (`semget` / `semop` / `semctl`)
- **Creation race**: two processes both calling `semget(key, n, IPC_CREAT)` succeed; only one should initialize. Pattern: one process creates with `IPC_CREAT | IPC_EXCL` and initializes; others use plain `semget`. Or use `SETVAL` with `semctl`.
- **`SEM_UNDO`**: lets the kernel reverse a process's semop if the process dies without releasing. Crucial if you don't want orphaned locks bringing down the system. Trade-off: requires the kernel to track per-process undo state.
- **`semop` with negative value blocks** if the result would be negative — the basic "P" operation. Make sure callers expect this and that you handle `EINTR` from signals.
- **Initialization is not atomic with creation.** Between `semget(IPC_CREAT)` and the `SETVAL`, another process can call `semop` and see semval = 0. Either initialize before any other process can know the key exists, or use a separate sync semaphore (chicken and egg…), or accept the standard idiom: creator initializes, others poll.
- **Cleanup**: `IPC_RMID` removes the set. Resources persist past process exit otherwise — check `ipcs` if you suspect leaks. `ipcrm` to clean up.

### System V message queues (`msgget` / `msgsnd` / `msgrcv`)
- **`mtype` selects messages**: `msgrcv` with `msgtyp=0` is FIFO; `>0` matches that type; `<0` gets the smallest type `≤|msgtyp|`. The PID-as-mtype pattern (client puts its PID; server replies with that PID as mtype) is correct but watch for PID reuse on long-running systems.
- **Size limits**: `MSGMAX` (per message) and `MSGMNB` (per queue) are tunable. Default 8 KiB / 16 KiB on Linux. Check, don't assume.
- **Blocking vs `IPC_NOWAIT`**: `msgsnd` blocks if queue full; `msgrcv` blocks if empty. Use `IPC_NOWAIT` for non-blocking and check `errno == EAGAIN`.
- **`EINTR`**: every blocking `msgop` can return `EINTR` on signal. Loop and retry, or use `SA_RESTART`.
- **Persistence**: queues survive process exit. Leak them and `ipcs -q` will grow.

### Shared memory (`shmget` / `shmat` / `shmdt`)
- Shared memory is **not synchronized** — you need a semaphore or mutex (a `pthread_mutex_t` with `PTHREAD_PROCESS_SHARED`) for any concurrent access.
- Pointers stored in shared memory are usually wrong in the other process — `shmat` may map at a different address. Store offsets, not pointers.
- **Atomicity**: writes larger than the machine word are not atomic; readers can see torn values.

### POSIX vs System V
POSIX IPC (`sem_open`, `mq_open`, `shm_open`) is generally nicer: filesystem-style names, better cleanup, `fd`-based, works with `select`/`poll` for the mq variant. Prefer it for new code unless coursework forces SysV (which is common in OS courses).

## Signals and forks

- `fork` in a multi-threaded program: only the calling thread survives in the child. Locks held by other threads are still "held" — call only async-signal-safe functions between `fork` and `exec`. Or use `pthread_atfork` carefully.
- Zombie processes: parent must `wait`/`waitpid` or set `SIGCHLD` to `SIG_IGN` (and accept losing exit status).
- Orphans get reparented to PID 1 (or the nearest subreaper). Fine, but don't depend on TTY/session being inherited.
- `SIGCHLD` is the standard "child died" signal; can coalesce, so always loop `waitpid(-1, ..., WNOHANG)` until it returns 0 or -1.

## Async / event-loop pitfalls (Python asyncio, JS, Tokio)

- Blocking call inside the event loop = whole program stalls. Find them: `time.sleep` (use `asyncio.sleep`), synchronous file I/O, synchronous DB clients, synchronous `requests` (use `aiohttp` / `httpx`).
- Unawaited coroutines / promises: `RuntimeWarning: coroutine ... was never awaited` is a real bug, not a warning. In JS, an unhandled promise rejection eventually kills the process.
- Cancellation: ensure `try/finally` to release resources when a task is cancelled mid-flight.
- Task groups / structured concurrency (asyncio.TaskGroup, trio nursery, Tokio's `JoinSet`): use them. They guarantee all spawned tasks are awaited and errors propagate.

## Senior questions on every concurrent review

1. List every piece of shared state. For each: who reads, who writes, what protects it?
2. For every compound operation (read-modify-write, check-then-act): is the *whole sequence* atomic?
3. List every lock. Is there a global ordering? Are any two locks ever held at once?
4. What happens on `EINTR`, `EAGAIN`, or a partial read/write?
5. On crash mid-operation, is state recoverable? Is there orphaned IPC?
6. On shutdown, who tells background work to stop, and how do we know it did?
