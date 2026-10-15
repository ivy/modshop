/* Restore (un-minimize) the game's main window from inside the same wine prefix. */
#include <windows.h>
#include <stdio.h>
static BOOL CALLBACK each(HWND h, LPARAM lp) {
    char title[256]; DWORD pid = 0;
    GetWindowTextA(h, title, sizeof title);
    GetWindowThreadProcessId(h, &pid);
    if (strcmp(title, "Star Wars: Knights of the Old Republic") == 0) {
        LONG style = GetWindowLongA(h, GWL_STYLE);
        printf("hwnd %p pid %lu style %08lx iconic %d\n", h, pid, style, IsIconic(h));
        if (IsIconic(h)) { ShowWindow(h, SW_RESTORE); printf("  restored -> iconic %d\n", IsIconic(h)); }
        SetForegroundWindow(h);
    }
    return TRUE;
}
int main(void) { EnumWindows(each, 0); return 0; }
