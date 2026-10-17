// A companion's own conversation: their recovery, while they are down.

#include "k_oaj_inc"

int StartingConditional()
{
    return IsDown(NpcOf(OBJECT_SELF));
}
