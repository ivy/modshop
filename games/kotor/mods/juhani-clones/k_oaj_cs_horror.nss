// The transformation, run by the grove cutscene's owner: she reaches for their minds with the
// Force, and both companions clutch their heads.

#include "k_oaj_inc"

void Horror(object oMember)
{
    AssignCommand(oMember, ClearAllActions());
    AssignCommand(oMember, ActionPlayAnimation(ANIMATION_LOOPING_HORROR, 1.0, -1.0));
}

void main()
{
    object oJuhani = Juhani();
    object oFirst = GetObjectByTag(NpcTag(SPECIAL_NPC_1));
    object oSecond = GetObjectByTag(NpcTag(SPECIAL_NPC_2));
    ActionPauseConversation();
    AssignCommand(oJuhani, ClearAllActions());
    AssignCommand(oJuhani, ActionCastFakeSpellAtObject(FORCE_POWER_FEAR, oFirst));
    DelayCommand(0.5, Horror(oFirst));
    DelayCommand(0.6, Horror(oSecond));
    ActionWait(4.0);
    ActionResumeConversation();
}
