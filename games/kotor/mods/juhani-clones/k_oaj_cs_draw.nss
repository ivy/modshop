// The transformation, run by the grove cutscene's owner: the three of them draw their sabers.

#include "k_oaj_inc"

void main()
{
    ActionPauseConversation();
    AssignCommand(Juhani(), ActionEquipMostDamagingMelee());
    int nClone;
    for (nClone = 1; nClone <= 2; nClone++) {
        AssignCommand(GetObjectByTag(CloneTag(nClone)), ActionEquipMostDamagingMelee()); // her blueprint carries it unequipped
    }
    ActionWait(2.5);
    ActionResumeConversation();
}
