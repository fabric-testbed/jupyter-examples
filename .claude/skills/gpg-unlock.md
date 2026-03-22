---
name: gpg-unlock
description: Cache GPG passphrase in gpg-agent for non-interactive commit signing
user_invocable: true
---

# /gpg-unlock — Cache GPG Passphrase for Signing

Cache the user's GPG passphrase in the gpg-agent so that `git commit -S` works non-interactively. The passphrase stays in agent memory only — never written to disk.

## Configuration

- **Signing key ID**: `68D279E0BD93F510`
- **Keygrip**: `15D675AEC97250DFCF5A86F9CA022521AEBDC5BC`
- **Binary**: `/usr/libexec/gpg-preset-passphrase`
- **gpg-agent.conf**: `allow-preset-passphrase` is enabled

## Workflow

### 1. Ask for the passphrase

Use AskUserQuestion to prompt the user for their GPG passphrase. The question should make clear that the passphrase will only be cached in gpg-agent memory and not written to disk.

### 2. Hex-encode and preset

Convert the passphrase to hex and feed it to the agent:

```bash
/usr/libexec/gpg-preset-passphrase --preset 15D675AEC97250DFCF5A86F9CA022521AEBDC5BC <<< "THE_PASSPHRASE"
```

The passphrase is cached indefinitely (until gpg-agent restarts).

### 3. Verify

Test that signing works:

```bash
echo "test" | gpg --batch --pinentry-mode loopback --sign --armor -u 68D279E0BD93F510 > /dev/null 2>&1 && echo "GPG signing works" || echo "GPG signing FAILED"
```

### 4. Report

Tell the user:
- Passphrase is cached in gpg-agent memory
- All `git commit -S` and `/commit` calls will now sign without prompting
- Cache persists until gpg-agent restarts (e.g., reboot or `gpgconf --kill gpg-agent`)
- To re-lock: `gpgconf --kill gpg-agent`

## Security Notes

- NEVER write the passphrase to any file
- NEVER echo or log the passphrase
- NEVER store the passphrase in a variable that gets printed
- The passphrase exists only in gpg-agent process memory
- After this skill runs, the passphrase is no longer in the conversation context
