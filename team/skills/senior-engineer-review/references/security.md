# Security Reference

A working checklist for finding vulnerability classes in code review. Not exhaustive — these are the ones that catch real bugs in real systems.

## Trust boundaries

Always identify, before anything else: **where does untrusted input enter, and where does it stop being untrusted?** Untrusted means anything from network, disk, env vars, argv, IPC from another process, deserialization, or an LLM.

Senior questions:
- Is validation at the boundary, or scattered? (Boundary wins — once inside trusted code, every caller has to remember.)
- Is "validated" a *type* or a *convention*? Types beat conventions.
- Is the same input parsed twice with different parsers? (Parser-mismatch bugs: HTTP request smuggling, JSON/YAML disagreement, normalization differences.)

## Injection family

All "X injection" bugs are the same bug: untrusted data parsed as code/control by a downstream interpreter. The fix is *always* the same shape: separate code from data using a parameterized API.

### SQL injection
- Never string-concatenate user input into SQL. Use parameterized queries / prepared statements.
- ORMs help but aren't immune — raw-SQL escape hatches, `LIKE` patterns, `ORDER BY <user input>` are common holes.
- Stored procedures are not automatic protection; they can still concatenate.

### Command injection
- `system()`, `exec` with `shell=True`, backticks — banned with untrusted input.
- Use exec-array form: `subprocess.run([cmd, arg1, arg2])`, not `subprocess.run(f"{cmd} {arg1}", shell=True)`.
- Even with exec-array, watch for path manipulation, argument injection via leading `-`.

### Template / SSTI
- Never feed user input as the *template*. Only as data.
- Jinja2, ERB, Handlebars, Razor — all have RCE if the template is attacker-controlled.

### LDAP, XPath, NoSQL, log injection, header injection, HTML/JS (XSS)
Same shape: parameterize, escape contextually, never trust.

### XSS specifically
- Context-aware escaping: HTML-body, attribute, JS, CSS, URL each need different escaping.
- `innerHTML = userInput` → XSS. Use `textContent`.
- CSP is defense in depth, not the primary fix.
- DOM-based XSS: sinks like `location`, `eval`, `setTimeout(str, ...)`, `document.write`.

## Authentication

- Password storage: Argon2id (preferred), scrypt, or bcrypt. **Never** raw SHA-256/SHA-512 — even with salt, it's GPU-cracking-fast. PBKDF2 only if FIPS-required.
- Don't roll session tokens — use the framework's. If you must: ≥128 bits of entropy from a CSPRNG (`secrets.token_urlsafe`, `crypto.randomBytes`, `getrandom`).
- Session fixation: regenerate session ID on login.
- Account enumeration: same response time and same message for "wrong password" vs "no such user."
- Password reset tokens: single-use, short-lived (≤1 hour), invalidated after use, bound to the account.
- MFA: TOTP is good; SMS is weak; recovery codes need the same protection as passwords.

## Authorization

- Check authz *at the resource layer*, not at the route layer. Route-only checks fail to IDOR (insecure direct object reference): `/api/orders/123` where you forgot to check `order.user_id == current_user.id`.
- Vertical (role-based) and horizontal (per-object) authz are different checks; need both.
- Default-deny, not default-allow. Adding a new endpoint should require *adding* permissions, not removing restrictions.
- "Forced browsing": admin pages that work without UI links — still authz-checked.

## Secrets

- Never in source control. Use a vault, KMS, or env vars at minimum.
- Never in logs, error messages, URL query strings, or referer headers.
- Never in core dumps — zero buffers after use in C/C++; use `mlock` or `securezero`.
- Rotation: build for it before you need it.
- API keys: scope them. A key that can do everything is a key that will leak everything.

## SSRF (Server-Side Request Forgery)

When the server fetches a URL the user provides:
- Validate the URL *after* DNS resolution, not before (TOCTOU via DNS rebinding).
- Block private ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16` (cloud metadata!), `::1`, `fc00::/7`, `fe80::/10`.
- Block redirects, or revalidate each hop.
- Set timeouts and response-size limits.
- In cloud: block `169.254.169.254` (AWS/GCP/Azure metadata) explicitly — it's the #1 SSRF target.

## Deserialization

Untrusted deserialization = remote code execution in most languages.
- Python: `pickle.loads` on untrusted bytes → RCE. Use JSON.
- PHP: `unserialize` → RCE. Use JSON.
- Java: `ObjectInputStream.readObject` → RCE. Use JSON + a strict schema.
- YAML: PyYAML's `yaml.load` → RCE. Use `yaml.safe_load`.
- JSON is generally safe *as parsing* but watch for prototype pollution in JS, and watch for what your code *does* with the parsed object.

## Path traversal

- Never join user input into a file path without normalizing and confirming the result is inside the intended directory.
- Don't blocklist (`../`) — attackers will use `..%2F`, `..\\`, UTF-8 overlong, normalization tricks.
- Allowlist: compute the canonical path (`os.path.realpath` / `filepath.Abs`), verify it has the intended prefix.

## TOCTOU (Time-Of-Check / Time-Of-Use)

- `if file_exists(x): open(x)` is a race. Use `open` with the right flags directly (`O_CREAT | O_EXCL`).
- Same shape on the web: "check user has access" then "do the operation" — bad if state can change between. Make the check atomic with the operation.

## Rate limiting & abuse

- Login, password reset, signup, API in general — all rate-limited per IP *and* per account.
- Resource-intensive endpoints (image processing, regex on user input, file upload): cap size, time, concurrency.
- ReDoS: user-supplied regex or user input fed to a backtracking regex can DoS. Use re2 or set a timeout.

## Cryptography choices

See `crypto.md` for the full deep-dive.

## Defensive coding patterns (the second layer)

Use these patterns to build the "if the primary defense fails, what catches it?" answer.

- **Fail-closed defaults.** Authorization checks return *deny* on error, not *allow*. Config parsers that can't read a setting return the most-restrictive default. Network rules whitelist what's allowed, not blacklist what's forbidden.
- **Allowlist > blocklist.** Blocklists are an enumeration of the threats you thought of; allowlists are an enumeration of the inputs you understand. Use allowlists wherever the input space is bounded (column names, file extensions, role names, redirect URLs, message types).
- **Least privilege.** DB users per service, with grants matching what the service does — read service can't `DELETE`. Filesystem perms `0600` when only the owner needs access. Capabilities or seccomp where applicable. `setuid` only where unavoidable and audited.
- **Separation.** Run the parser separately from the executor. Run untrusted code in a sandbox / container / separate user. Keep secrets in a separate process or vault.
- **Make the wrong thing hard.** Type the "trusted" version of data differently from the "untrusted" version — a `SafeHTML` type that can only be constructed by the sanitizer, a `UserID` type that can only be constructed from an authenticated session. The compiler enforces what code review forgets.
- **Loud failure.** Log on every security-relevant decision (denied access, missing token, invalid signature). Alert on anomalies (sudden 401 spike = credential stuffing in progress). Silent failures are second-layer failures.
- **Reversibility.** Soft-delete with retention. Audit log before destructive operations. Real backups, restore-tested.
- **Idempotency.** Operations safe to retry — payment APIs with idempotency keys, queue handlers tolerating redelivery. Without it, "second layer" retry logic creates new bugs.

## Senior questions to ask on every security review

1. What's the threat model? (Who is the attacker, what's the asset, what's the trust level of the input?)
2. Where's the trust boundary, and is validation *there* or scattered?
3. What's the worst case if every assumption in this code is wrong simultaneously?
4. If this code logs the wrong field, do secrets leak?
5. If this code crashes mid-operation, is state consistent?
6. Is this defense in depth, or the only line of defense? (Both are fine; just know which.)
