// Juhani's conversation (dan14_juhani): her defeat after the clones' fight, in place of the game's
// opening line, which k_pdan_anger20 offers once by the same flag.

int StartingConditional()
{
    if (GetGlobalBoolean("OAJ_SPECIAL") && !GetGlobalBoolean("DAN_JUHANIF_DONE")) {
        SetGlobalBoolean("DAN_JUHANIF_DONE", TRUE);
        return TRUE;
    }
    return FALSE;
}
