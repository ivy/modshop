// A silent beat in a conversation, run by its owner.

void main()
{
    ActionPauseConversation();
    ActionWait(1.5);
    ActionResumeConversation();
}
