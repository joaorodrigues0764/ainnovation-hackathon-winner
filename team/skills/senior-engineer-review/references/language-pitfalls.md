# Language-Specific Pitfalls

Common traps grouped by language. Use as a checklist when reviewing code in each language.

## C

### Memory safety
- **Bounds**: every array index, every pointer arithmetic. Off-by-one is the default state of a `for` loop.
- **Use-after-free**: pointer aliasing, `realloc` invalidating earlier pointers, freeing in one branch and using in another, returning a pointer to a stack variable.
- **Double-free**: paired with NULL-after-free as defense (but doesn't help across threads).
- **`strncpy` does not NUL-terminate** if the source is ≥ n bytes. Use `snprintf` or write your own bounded copy.
- **`gets` is gone** (rightly). **`sprintf`** is dangerous; prefer `snprintf` and check the return.
- **`strcat`/`strcpy`** banned in new code.

### Undefined behavior to watch for
- Signed integer overflow (UB; the compiler will optimize as if it can't happen).
- Reading uninitialized stack memory.
- Aliasing: same memory accessed through differently-typed pointers (strict aliasing).
- Modifying a string literal: `char *s = "hi"; s[0] = 'H';` is UB.
- `if (p && p->x)` is correct; `if (p->x && p)` is UB.
- Comparing pointers that aren't into the same object.
- `INT_MIN / -1` traps.

### Integer pitfalls
- `size_t` is unsigned; `(size_t)-1` is huge, not negative.
- Mixing signed and unsigned in comparisons: `if (signed_var < unsigned_var)` converts signed to unsigned.
- `int` overflow truncating to `short` / `char` silently.
- `sizeof` is `size_t`; printing with `%d` is wrong, use `%zu`.

### Error handling
- Check every fallible call: `malloc`, `fopen`, `read`, `write`, `fork`, `pipe`, `semget`, `msgsnd`...
- `errno` is only meaningful right after a syscall returns -1. Save it if you do anything else first.
- Loop on `EINTR` for blocking syscalls (or use `SA_RESTART`).
- `read` and `write` can return fewer bytes than requested — always loop.

### Resource cleanup
- The classic goto-based cleanup chain is idiomatic and good. Don't be shy of it.
- File descriptors close on `exec` unless you set `FD_CLOEXEC`; matters if you `fork` and don't `exec` immediately.
- Always pair `malloc/free`, `fopen/fclose`, `open/close`, `pthread_mutex_lock/unlock`, `shmat/shmdt`, etc.

### Format string and printf family
- **Never** `printf(user_input)`. Always `printf("%s", user_input)`. Format-string vulns = arbitrary read/write.
- Mismatched format and argument types: `%d` for `long`, `%s` for an int, `%u` for negative — UB or garbage.

## C++

All of the C list, plus:
- **RAII first**: every resource in a destructor-owning type. `std::unique_ptr`, `std::lock_guard`, `std::scoped_lock`, your own.
- **Rule of zero / three / five**: if you write any of destructor / copy ctor / copy assign / move ctor / move assign, think about whether you need all of them.
- **Slicing**: passing a derived object by value to a base parameter loses the derived parts.
- **References vs pointers**: references can't be null, can't be reseated — prefer when applicable.
- **`auto&` vs `auto`**: `auto` in a range-for over a non-trivial container copies; use `const auto&` by default.
- **Static initialization order fiasco**: file-scope globals across translation units. Avoid global state; if forced, use Meyers singletons (`static T& get() { static T t; return t; }`).
- **Iterator invalidation**: `vector::push_back` can invalidate all iterators; `map::erase` invalidates that one. Read your container's rules.
- **`shared_ptr` cycles** leak. Break with `weak_ptr`.

## Python

### Common bugs
- **Mutable default arguments**: `def f(x=[])` shares the list across calls. Use `None` and create inside.
- **Late binding in closures**: `[lambda: i for i in range(3)]` all print 2. Capture explicitly: `lambda i=i: i`.
- **`is` vs `==`**: `is` is identity. `x is 5` works only for small-int cache; never depend on it.
- **`except:` bare** catches `SystemExit`, `KeyboardInterrupt`. Use `except Exception:` at minimum.
- **`open(path)` without context manager**: file leaks on exception. Always `with open(...) as f:`.
- **`pickle.loads` on untrusted data**: RCE. Use JSON.
- **`subprocess` with `shell=True`** on user input: command injection. Use a list and `shell=False`.
- **`eval` / `exec`** on user input: RCE. Don't.
- **`yaml.load`**: RCE. Use `yaml.safe_load`.

### Concurrency
- **GIL** does not make compound operations atomic. `counter += 1` across threads still races.
- `threading.Lock()` not `threading.lock()`.
- `multiprocessing` pickles arguments — large args, non-picklable objects fail.
- `asyncio` — never call blocking I/O in an `async def`; never call `time.sleep`; never `requests.get`. Use `asyncio.sleep`, `aiohttp`/`httpx`.

### Subtle wrongs
- **`==` on floats**. Use `math.isclose`.
- **Integer division: `/` vs `//`** in Python 3.
- **`dict` iteration order** is insertion order since 3.7 — relying on it is fine now, but not in older code.
- **`copy.copy` vs `copy.deepcopy`**: shallow vs deep. Default-mutable nested structures bite.

## JavaScript / TypeScript

### Classic bugs
- **`==` vs `===`**: always `===` and `!==` unless you specifically want coercion.
- **`this` binding**: `function` callbacks lose `this`; arrow functions inherit it. Pick deliberately.
- **`var` is hoisted** to function scope. Use `const` by default, `let` when reassigned, `var` never.
- **`for...in` enumerates** enumerable keys including inherited. Use `for...of` with `Object.keys` or `Object.entries`.
- **`typeof null === "object"`**. Special-case it.
- **`NaN !== NaN`**. Use `Number.isNaN`.
- **`parseInt("08")`**: in old JS without radix, octal. Always pass a radix: `parseInt(s, 10)`.

### Async
- **Unhandled rejections**: a Promise without `.catch` or an `await` without `try`. Will eventually crash Node.
- **`forEach` doesn't await**: `arr.forEach(async x => await f(x))` does not wait. Use `for...of` or `Promise.all(arr.map(...))`.
- **Floating promises** in handlers: `void promise` if intentional, otherwise await or `.catch`.
- **Race in `async` series with shared state**: each `await` is a suspension point where other code can interleave.

### Security
- **`innerHTML = userInput`**: XSS. Use `textContent`.
- **`dangerouslySetInnerHTML`** in React: only with sanitized input.
- **`eval`, `new Function`, `setTimeout(string, ...)`** with user input: RCE in browser.
- **Prototype pollution**: `Object.assign({}, JSON.parse(userInput))` if input is `{"__proto__": {...}}`. Use `Object.create(null)` or freeze prototypes.
- **`fetch` without HTTPS**, no cert checking on Node clients, no `credentials` policy.

### TypeScript-specific
- **`any` is a defeat**. Prefer `unknown` and narrow.
- **`as` casts** bypass the type system — sometimes necessary, always suspicious.
- **`!` non-null assertion** is the same: a promise to the type checker, no runtime check.
- **`strictNullChecks` off**: makes the type system half-useless. Turn it on.

## SQL

### Injection
- **Parameterize**. Always. `WHERE x = ?` not `WHERE x = '"+x+"'`.
- `ORDER BY <user input>` can't be parameterized — allowlist column names.
- `LIKE` with user input: escape `%` and `_`.

### Correctness
- **`NULL` propagates**: `x = NULL` is never true; use `x IS NULL`.
- **`NOT IN (subquery)`** with any NULL in the subquery returns empty. Use `NOT EXISTS`.
- **Implicit type conversion** in comparisons can silently change query plans and miss rows.
- **`GROUP BY`** with non-grouped non-aggregated columns: undefined behavior in many DBs; explicit error in modern ones.

### Performance
- **N+1**: looping in app code over individual queries instead of one JOIN.
- **Missing index** on a `WHERE`, `JOIN`, or `ORDER BY` column — `EXPLAIN` it.
- **Index on a function-of-column** in the `WHERE`: `WHERE LOWER(email) = ?` won't use an index on `email`. Use a functional index or store the lowered form.
- `SELECT *` in production: schema changes break consumers, transfers bytes you don't need.

### Transactions
- **Isolation level**: default is often `READ COMMITTED`; concurrent updates can lose. `SERIALIZABLE` for accounting-grade correctness; `REPEATABLE READ` is the middle.
- **Long transactions** hold locks and bloat MVCC versions.
- **Application-level retry** for serialization failures — don't catch and ignore.

## Go

- **Goroutine leak**: any `go` without a way to signal it to stop. Use `context.Context`.
- **`for i, v := range slice` + `go func(){ ... v ... }()`**: `v` is reused; all goroutines see the last value. Pass as parameter.
- **`defer` in a loop** stacks up until function return; use a named helper if cleanup must happen per-iteration.
- **`nil` map writes panic**, `nil` slice appends work. Know the difference.
- **Error wrapping** with `%w` since Go 1.13. Use it; check with `errors.Is`/`errors.As`.
- **Channel direction** in signatures: `<-chan T` (receive), `chan<- T` (send). Use them; bare `chan T` is rare.
- **Closing a channel** is for "no more values coming" — only the sender does it, never the receiver, never twice.
- **`time.After` in a `select` loop** leaks until the timer fires; use `time.NewTimer` and `Stop` it.

## Rust

- **`unwrap` / `expect`** in library code is a panic-shaped landmine. Return `Result`.
- **`as` casts** truncate silently; use `try_into` for fallible.
- **`Rc<RefCell<T>>` cycles** leak — same as `shared_ptr` cycles.
- **`Mutex` poisoning**: lock returns `Result`; a panic while held poisons the lock. Decide whether to recover or propagate.
- **`async` without `Send`**: spawning needs `Send`; capturing a non-`Send` (`Rc`, `RefCell`) across an `.await` breaks it.
- **`std::mem::transmute`** is almost always wrong. There's a safe alternative.
- **`unsafe`** must have a comment explaining *why* the invariants hold.

## Shell / Bash

- **Always quote variables**: `"$var"` not `$var`. Unquoted = word-splitting + globbing on the value.
- **`set -euo pipefail`** at top of scripts. `-e` exit on error, `-u` error on undefined, `-o pipefail` propagate pipe errors.
- **Use `[[ ]]` not `[ ]`** in bash; safer parsing.
- **`eval` on user input**: RCE.
- **`rm -rf "$dir/"`** with empty `$dir`: erases `/`. Use `set -u` and validate.
- **Word-splitting in `for x in $(cmd)`**: prefer `while read` with `IFS` set.
