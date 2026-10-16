# 10: no self-minimise when the game loses activation

About one start in three under Proton in Steam's Game Mode stopped on a black screen right after the logo movies, and the game never reached the main menu. Read from the hung process on the handheld (2026-10-16):

- **The main thread was presenting a frame.** The game's main loop called `SwapBuffers(GetDC(hwnd))` (return address `0x004048C7`); under it, Mesa's DRI3 code was waiting for a free back buffer that never came (`st_framebuffer_validate` → `loader_dri3_get_buffers` → `dri3_find_back` → `dri3_wait_for_event_locked` → `xcb_wait_for_special_event`). Every other thread was idle.
- **The window was minimised.** The game window's Win32 style (`_WINE_HWND_STYLE` on its X window) was `0xB6000000`; on a good start it is `0x96000000`. The difference is `WS_MINIMIZE`. Wine had sized its OpenGL child window to the minimised client rectangle, 160x31, where a good start has 1920x1080. Wine updates that child's size after `glXSwapBuffers` returns, so the stuck swap could never correct it.
- **The game minimised itself.** Its window procedure (`0x00402800`) handles `WM_ACTIVATEAPP` at `0x00402951`. On a deactivation, while the render window's fullscreen flag (`+0xAC`, set by its mode switch after `ChangeDisplaySettingsA`) is 1, it calls `ShowWindow(hwnd, SW_MINIMIZE)` at `0x004029DB`, then restores the gamma ramp and the desktop's mode. On Windows that is how Alt-Tab leaves a fullscreen game; in Game Mode there is no taskbar, and the restore would run on the thread stuck in the swap.
- **The logo movie's window is what deactivates it.** The movie plays in its own window, and its handoff to the game window under gamescope is the deactivation; skipping the logos was the trigger reported on 2026-10-15. The Steam and quick-access overlays do not deactivate the game (watched with the window's style logged every 100 ms).

The game ran its fullscreen path although `swkotor.ini` said `FullScreen=0`: the flag at `+0xAC` read 1 and the window had the fullscreen popup style. What overrides the setting is not known.

`make.py` adds a KPM `simple` hook to the `kmrp` block of `patch_config.toml` that replaces the call's nine bytes (`push 6; push ecx; call [ShowWindow]` at `0x004029D8`) with NOPs; the stack stays balanced, and the gamma and mode restore after it still run. The same change, written into the running game's memory on every start, was played: two starts and the session before them reached the menu, and the window's style never showed `WS_MINIMIZE`. Two clean starts at one hang in three happen by chance 44% of the time, so the count is still short of proof; the mechanism is read end to end.

KMRP patch 0006 in [`../../patches/kmrp/`](../../patches/README.md) makes the change upstream, as a core hook at `0x004029D2` that skips the call only under Wine. The installed `kmrp.dll` is KMRP's release, so its hooks reach this build only with a release that carries them; when one does, `make.py` finds `KeepWindowOnDeactivateK1` there and does nothing, and this folder can go.

```bash
python3 repairs/10-no-minimize-under-proton/make.py /path/to/swkotor
```
