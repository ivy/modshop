// The transformation, run by the grove cutscene's owner: the next companion still in the party
// becomes a clone of her, Carth first, then Mission.

#include "k_oaj_inc"

void main()
{
    object oFirst = GetObjectByTag(NpcTag(SPECIAL_NPC_1));
    object oSecond = GetObjectByTag(NpcTag(SPECIAL_NPC_2));
    ActionPauseConversation();
    if (IsNPCPartyMember(SPECIAL_NPC_1)) {
        AssignCommand(Juhani(), Transform(oFirst, 1));
    } else {
        AssignCommand(Juhani(), Transform(oSecond, 2));
    }
    ActionWait(2.0);
    ActionResumeConversation();
}
