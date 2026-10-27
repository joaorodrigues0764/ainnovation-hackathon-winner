# Cryptography Reference

The single most important rule: **don't roll your own crypto.** Use vetted libraries (libsodium / NaCl, your platform's TLS library, your language's standard crypto module). Most "crypto bugs" in this checklist exist because someone reached past the safe API and built primitives by hand.

The second rule: **misuse-resistant APIs over flexibility.** If a library offers both a "secret box" (one-call authenticated encryption with a key) and a la carte primitives, use the secret box.

## Choosing a primitive

| If you need... | Use | Notes |
|---|---|---|
| Symmetric encryption of a message | **AES-256-GCM** or **ChaCha20-Poly1305** | Both are AEAD (authenticated). Never ECB. Never raw CBC. Never CTR without a MAC. |
| Encrypt large file / streaming | XChaCha20-Poly1305 with chunked construction, or AES-GCM-SIV | Naïve AES-GCM has a 64 GiB-per-key limit and is nonce-misuse-fatal. |
| Hash for integrity (not passwords) | **SHA-256**, **SHA-512**, **BLAKE2**, **BLAKE3** | MD5 and SHA-1 are broken — fine only as legacy checksums, never for security. |
| Hash a password | **Argon2id** (preferred), **scrypt**, **bcrypt** | Tunable cost. PBKDF2 only if compliance demands. |
| Derive a key from another key | **HKDF** (with SHA-256) | Not for passwords. |
| Derive a key from a password | **Argon2id** or **scrypt** | Yes, same algorithms as password hashing. |
| MAC (authenticate a message) | **HMAC-SHA-256** or **Poly1305** (with a unique nonce) | Don't invent. |
| Random tokens, session IDs, salts, nonces | OS CSPRNG: **`getrandom`**, **`/dev/urandom`**, **`secrets`** (Py), **`crypto.randomBytes`** (Node), **`crypto/rand`** (Go) | Never `rand()`, `Math.random()`, `random.random()`. |
| Public-key encryption | **X25519** key exchange + AEAD, or libsodium's `crypto_box` | RSA-OAEP is acceptable but slower and footgun-prone. |
| Signatures | **Ed25519** | RSA-PSS or ECDSA acceptable. **Never** RSA PKCS#1 v1.5 for new code. |
| Key exchange | **X25519** (or X448) ECDH | Diffie-Hellman over finite fields only with ≥2048-bit safe primes. |
| TLS | **TLS 1.3**, fall back to 1.2 if forced. Disable 1.0/1.1, SSLv3. | Don't implement TLS yourself. |

## Nonces and IVs

This is where most "I used AES-GCM correctly" code is actually wrong.

- **AES-GCM:** nonce **must** be unique per key. Repeat = catastrophic (key recovery for the authentication, plaintext recovery for the confidentiality). 12-byte random nonce is OK for ≲2³² messages; for more, use a counter.
- **AES-GCM-SIV** and **XChaCha20-Poly1305:** misuse-resistant — repeated nonce only reveals that two ciphertexts had the same plaintext. Prefer these if you can't guarantee uniqueness.
- **CBC mode:** IV must be unpredictable (random), not just unique. CBC + predictable IV = BEAST-style attacks.
- **CTR:** counter must never repeat for a key. Same catastrophe as GCM nonce reuse.
- Never derive a nonce from the message (that's just a hash; defeats the point).

## Constant-time operations

Comparing secrets with `==` leaks length and prefix through timing.

- Python: `hmac.compare_digest`
- Node: `crypto.timingSafeEqual` (buffers of equal length)
- Go: `crypto/subtle.ConstantTimeCompare`
- C: implement bit-OR-accumulator loop, or use libsodium `sodium_memcmp`.

Same applies to: HMAC verification, password hash comparison, token equality, anything where an attacker controls one side.

## Key management

- **Generation:** CSPRNG. Always.
- **Storage:** OS keychain, KMS (AWS/GCP/Azure), HSM, or libsodium's secret-storage. Never in source. Never in env vars if you have a better option (they leak into logs, child processes, `/proc`).
- **Rotation:** design for it. Encrypt with a *data encryption key* (DEK), encrypt the DEK with a *key encryption key* (KEK), rotate the KEK without re-encrypting all the data.
- **Wiping:** in C/C++, zero buffers after use. The compiler will eliminate naïve memsets — use `explicit_bzero`, `SecureZeroMemory`, `sodium_memzero`.
- **Logging:** keys must never be loggable. If your config struct has a `Secret` field, override its `Display`/`__repr__` to print `***`.
- **Lifetimes:** scope keys to the smallest reasonable lifetime. Per-session keys, per-message keys (with KDF), forward secrecy where possible.

## Password handling

```
plaintext password ──[Argon2id, with random salt, sufficient cost]──> hash
```

- **Argon2id** parameters (start here, tune to ≥250ms on your hardware):
  - memory: 64 MiB
  - iterations: 3
  - parallelism: 1
- **bcrypt:** cost ≥12. Note: bcrypt silently truncates at 72 bytes; pre-hash with SHA-256 if you accept longer.
- **scrypt:** N=2¹⁵, r=8, p=1 minimum.
- **Salt:** unique per password, stored alongside the hash. (Modern libraries do this automatically.)
- **Pepper:** optional extra secret mixed in before hashing, stored separately from the DB. Defense in depth.
- **Verify** with constant-time comparison (the library function, never `==`).
- **Don't pre-hash** with a fast hash unless you understand why bcrypt's 72-byte limit forces you to.

## Crypto pitfalls — frequent finds

1. **ECB mode** anywhere. Penguin image. Visible patterns. Critical finding.
2. **MD5 or SHA-1** for anything security-relevant. Critical for signatures/HMAC; merely "stale" for non-security checksums.
3. **`Math.random()` / `rand()` / `random.random()`** for tokens, IDs, salts, nonces. Critical.
4. **Static IV** in CBC or counter in CTR. Critical.
5. **Custom XOR "encryption"** with a repeated key. Critical.
6. **Comparing HMACs/tokens/hashes with `==`**. High (timing oracle).
7. **Raw SHA-256(password + salt)** as password storage. High — GPU cracks it in hours.
8. **Verifying JWT with the wrong algorithm**: accepting `alg: none`, or accepting HS256 when the key is the RSA public key. Critical.
9. **Forgetting to verify TLS certificates** (e.g., `InsecureSkipVerify: true`, `verify=False`). Critical in production code.
10. **Encryption without authentication** (CBC alone, CTR alone). High — padding oracles, bit-flipping attacks.
11. **Using the same key for encryption *and* authentication** — separate them with HKDF.
12. **Long-lived JWTs without revocation strategy.** Medium-to-high depending on what they grant.

## Senior questions on any crypto review

1. What primitive, what mode, what nonce strategy? Name all three.
2. Where does the key come from, where does it live, who can read it?
3. Is the API misuse-resistant or à la carte?
4. What's the failure mode if the nonce repeats? If the key leaks? If the algorithm is later broken?
5. Is this encryption providing confidentiality alone, integrity alone, or both? Are you sure?
6. Could a downgrade attack force a weaker algorithm?
7. Is anything compared with `==` that an attacker controls?
