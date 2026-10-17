// Mission's recovery: she sends the player to Carth only while he is still down.

#include "k_oaj_inc"

int StartingConditional()
{
    return IsDown(NPC_CARTH);
}
