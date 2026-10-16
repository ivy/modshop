---
title: Runtime trace
priority: p4
status: idea
depends_on: [crash-capture]
---

# Runtime trace

Record which resources the game reads while it runs, so a crash comes with the last few resources loaded before it.

## The problem

Static tools say what is in the build; they do not say what the game was doing when it died. Repair 07 is a candidate rather than a proven fix because the difference between runs that crashed and runs that did not may be the session's history, not the texture ([its README](../../repairs/07-kmrp-pot-gui-textures/README.md)). Repair 08 was tied to a room by reasoning about what was in view from a door ([its README](../../repairs/08-wounded-republic-detonate-controller/README.md)). A record of what was loaded would have pointed at both directly.

## The idea

Trace the game's file reads on the handheld and map them to resources:

- loose files in `Override` show up as opens by name;
- resources inside archives (`.mod`, `.rim`, `.erf`, and the BIFs behind `chitin.key`) show up only as reads of the archive at an offset, but the archive's own table gives each resource's offset and size, so a read maps back to a resource name.

The output is a timeline of resources, kept with the run's [crash capture](crash-capture.md); its last entries before a crash are the first suspects. With the [asset index](asset-index.md), each suspect comes with the mod that introduced it.

## Unknowns

- Whether `strace` (or `bpftrace` on read syscalls with offsets) can attach to the game under Proton, and what it costs in frame rate.
- Whether the game reads archives with seeks and reads that map cleanly to resources, or through memory-mapped files that a syscall trace does not see.
- Whether Wine's own file-access debug channel is a cheaper source than syscalls.

## First step

`strace -f -e trace=openat,read,pread64,lseek` on the game for the first minute of a load, then check whether one known resource inside a module archive can be identified from the offsets alone.
