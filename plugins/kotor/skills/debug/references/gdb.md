# A native stack at the crash

gdb attached to the running game, stopping only at glibc's abort, recording every thread's stack, the registers, the raw stack and the library map, then killing the game, which is already aborting. One reproduction costs the player real time; this makes it count.

## Before asking anyone to reproduce

1. **Prove the capture on a dummy process first**, on the device: `sleep 600 &`, attach the same way, `kill -ABRT` it, and check the output reaches `=== DONE ===` and gdb exits. Every failure below was found this way or, worse, by a lost reproduction.
2. **Copy the game's libraries while it runs.** After the crash `/proc/<pid>/root` is gone, and gdb may not have symbolized everything:
   ```bash
   cp /proc/$PID/maps maps.txt
   awk '$6 ~ /\.so/ {print $6}' /proc/$PID/maps | sort -u | while read -r p; do
     mkdir -p "libs$(dirname "$p")"; cp "/proc/$PID/root$p" "libs$(dirname "$p")/"; done
   ```
   (About 90 files, 300 MB, for KotOR under Proton 11.)
3. **Attach, then confirm** `TracerPid` in `/proc/$PID/status` is gdb's pid and stays so for 30 seconds while the game runs. Only then tell the player to go.

## The attach

`scripts/catch-abort.gdb` (in this skill's directory), copied to the device and fed so gdb's input stays open:

```bash
{ printf 'set sysroot /proc/%s/root\nfile /proc/%s/exe\n' $PID $PID; cat catch-abort.gdb; sleep 86400; } \
  | gdb -q -nx -p $PID > capture.txt 2>&1
```

Run it detached (`setsid nohup sh -c '...' &`) so the ssh session can end. After the crash, kill the leftover `sh` and `sleep 86400` **by pid**, not by pattern.

Why each part, from what failed:

- **Not `-batch`.** In batch mode `continue` returned at once and gdb detached, twice, with no message.
- **Nothing queued after `continue` on gdb's input.** A non-batch gdb reads its input while the game runs; a `quit` queued there detached it before the crash, and the reproduction was lost. The capture lives in the catchpoint's `commands`.
- **An error inside a command list abandons the rest of it.** Reading 8192 words above `$sp` runs into unmapped memory, which silently skipped `kill` and `quit`; the script wraps that read in Python `try`.
- **`set sysroot /proc/<pid>/root` and `file /proc/<pid>/exe`.** Without them gdb reads files through `target:`, gets "Input/output error" on the preloader inside the container, and has no executable.
- **Pass Wine's signals.** Wine raises and handles SEGV, ILL, BUS, FPE, TRAP and USR1/2 for its own exceptions; stopping on them stops the game constantly. Only SIGABRT stops.
- **`set debuginfod enabled off`.** Otherwise gdb asks, or downloads for minutes.

## Symbols afterwards

gdb on the device has symbols for little: Mesa, the Steam Runtime's libc and Wine's Unix libraries mostly show `?? ()`. With `maps.txt` and the copied libraries:

```bash
python3 SKILL_DIR/scripts/symbolize.py maps.txt libs ADDR...
```

It maps each address to its library and file offset, converts the offset to a virtual address through the program headers, and names the function from `.symtab`, the embedded `.gnu_debugdata` mini symbol table, or `.dynsym`. Fedora-style builds (Bazzite's Mesa among them) carry `.gnu_debugdata` even where the distribution's debuginfod has no entry for the build-id; Bazzite's Mesa build-id was not on Fedora's debuginfod.

With no backtrace at all, the return addresses are still in the raw stack: every word that falls inside an executable mapping is a candidate frame. Read them top down and expect stale frames among the live ones.

## Reading the stack

- The frames under glibc's abort are where the corruption was **noticed**. Name them as the victim, not the cause.
- Read for what the code was doing: for example `u_default_texture_subdata → si_texture_transfer_map → si_texture_create_object → amdgpu_bo_create → pb_slab_alloc` is radeonsi allocating memory to upload a texture, so a texture upload was in progress, not necessarily at fault.
- Frames at `0x00400000`-`0x008C3000` are the game's own; name them from the dumped executable ([`engine.md`](engine.md)).

## Breakpoints in the game's code: not yet reliable

The catchpoint above stops only once, at the abort. Breakpoints that log and continue (`gdb.Breakpoint` whose `stop()` returns `False`, set on the game's own code with the same signal handling) did not hold up under Wine: on one attach gdb logged a single hit and then detached on its own; on the next, the game froze (video stopped, audio went on, no input) until gdb was sent `SIGHUP`, which detached it. Why is not established. Until it is, answer "which branch does the engine take" another way first: the decompiled code ([`engine.md`](engine.md)) for what a branch tests, and a save for the state it tests ([`evidence.md`](evidence.md), "A creature's state in a save"). Each attempt costs the player a session.
