# restore-window: un-minimize the game under gamescope

KotOR minimizes its own window when it loses focus in fullscreen. In Game Mode there is no taskbar, so that is a black panel with the game still running behind it (seen 2026-10-15 after skipping the startup logo movie: KMRP's movie window closed, gamescope logged `xwm: waylandres but no win`, the game's window went iconic with `WS_MINIMIZE` set).

`restore.exe` runs inside the game's wine prefix, finds the window titled "Star Wars: Knights of the Old Republic", and calls `ShowWindow(SW_RESTORE)` on it. Built with the llvm-mingw image:

```bash
podman run --rm -v "$PWD:/w:Z" docker.io/mstorsjo/llvm-mingw:latest sh -c 'cd /w && i686-w64-mingw32-clang -O1 -o restore.exe restore.c'
```

Run on the handheld with Proton's wine against the live prefix (gamescope's game display is `:1`):

```bash
P="$HOME/.local/share/Steam/steamapps/common/Proton 11.0"
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/32370/pfx WINEDLLPATH="$P/files/lib/wine" \
  WINEESYNC=1 WINEFSYNC=1 WINENTSYNC=1 DISPLAY=:1 XDG_RUNTIME_DIR=/run/user/$(id -u) "$P/files/bin/wine" restore.exe
```

If gamescope still shows nothing afterwards, `xdotool windowunmap <id>; xdotool windowmap <id>` on `:1` makes Xwayland re-announce the window's surface, after which gamescope refocuses it; whether the picture then returns was not confirmed the one time it was tried, because the game was stopped from Steam first.
