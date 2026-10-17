// The grove cutscene's EndConversation (dan14_cutjuh): Juhani turns on the party, as in the game.
// After the last insult her clones fight with her (k_oaj_fight), and she has spoken her own line;
// otherwise dan14ac_cutobj02 gives the battlecry the game gives on her way to her mark
// (k_pdan_juhani36).

void main()
{
    object oJuhani = GetObjectByTag("dan14_juhani");
    if (!GetGlobalBoolean("OAJ_SPECIAL")) {
        SignalEvent(GetObjectByTag("dan14ac_cutobj02"), EventUserDefined(110)); // "I will be your doom!"
    }
    SignalEvent(oJuhani, EventUserDefined(80));
    if (GetGlobalBoolean("OAJ_SPECIAL")) {
        ExecuteScript("k_oaj_fight", oJuhani);
    }
}
