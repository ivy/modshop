# Conventions

What every game directory in this repository follows, and why.

## Nothing from a game or a mod is committed

Game files belong to their publisher and mod files to their authors; most mod sites forbid redistribution, and the ones that allow it still want credit and a link. So this repository holds only what we wrote: scripts, patches to open-source tools, documentation. Everything else is input, fetched by the person building from the sources that offer it, and lives under `games/<game>/data/`, which `.gitignore` excludes whole.

This is also what makes the result reproducible. A build that depends on a file somebody edited by hand once cannot be repeated; a build that extracts the mod's file from the mod's own archive and patches it by script can be repeated by anyone with the archive. A "repair" here is therefore always a script plus a README, never a repaired file.

## No device identity

Hostnames, user names, home directories, Steam account ids and private network names stay out of git. `local.toml` (gitignored, with `local.example.toml` as the template) holds them for the person and the agent working on a given machine; the documents refer to "the handheld" (the machine that runs the game) and "the build host" (the machine that assembles the modded install). Paths in documents are written relative to those roles, with `$HOME` rather than a user's home.

## Reproducible, idempotent, scripted

The modded install is assembled by script from a pristine copy of the game and the mod archives, with every step recorded. A fix is applied in the tool that was wrong (as a patch series) or in the mod's file (as a build-time repair), not by editing the game folder, and not by removing the mod. The scripts can be rerun: a finished step is skipped, a stopped run resumes.

Copy-on-write copies are the cheap way to keep reference points: `cp -a --reflink=always` of a game folder is instant and takes no space on btrfs or XFS, so a pristine copy and a known-good copy sit beside the live one and a rollback is a rename.

## Patch series for other projects

A fix to another project (a modding library, a mod's own source) is a branch over the upstream commit it was written against, in a clone of that project, one commit per fix with the reason in the message, exported with `git format-patch` into `games/<game>/patches/<project>/`. The series' README states the project, the base commit, the branch name and how the series is applied. Upstreaming is the goal; once a patch is merged it leaves the series on the next rebase.

## Documents are for a reader with no context

Each game's README is the complete procedure: prerequisites, where the inputs come from, the steps in order, what to check, what goes wrong. Diagnosis notes sit beside the thing they explain. Documents describe the current state, not their own history.
