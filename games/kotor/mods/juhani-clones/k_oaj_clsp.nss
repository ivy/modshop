// OnSpawn of Juhani's clones (oaj_juhani1, oaj_juhani2): the default AI, and a body that stays
// where it fell until the fight is over (k_oaj_inc's EndFight).

#include "k_inc_generic"

void main()
{
    SetIsDestroyable(FALSE, FALSE, FALSE);
    GN_SetDayNightPresence(AMBIENT_PRESENCE_ALWAYS_PRESENT);
    GN_SetListeningPatterns();
}
