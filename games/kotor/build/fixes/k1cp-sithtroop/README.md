# k1cp-sithtroop

A one-line TSLPatcher change applied right after the Community Patch: the Sith trooper template `g_sithtroop007.utc` inside `modules/manm27aa.mod` gets `Appearance_Type=44`. The Community Patch's own installer fails on that one edit under HoloPatcher (its run is allowed one error in the manifest); this applies the edit it meant to make. Ours, not the mod's, which is why it lives in the repository and not in an archive folder.
