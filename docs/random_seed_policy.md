# Random Seed Policy

## Purpose

Seeds make computational comparisons auditable. They do not turn a simulated
trajectory into a biological replicate and they do not remove all native
backend nondeterminism.

## Seed generation

- Generate seeds from a declared campaign list or an explicitly recorded
  source; never recover or guess a seed after a run.
- Use non-negative integer seeds and record the complete list before execution.
- Assign each condition/replicate a stable seed identity. Do not reuse a seed
  accidentally across conditions when independent variation is intended.
- Store the campaign configuration, seed list, git commit, runtime report, and
  output directory together.

## Seed reuse

- Reuse the same seed only for a declared paired comparison, deterministic
  replay, or controlled ablation.
- Use different declared seeds for repeated stochastic conditions.
- Keep the distinction between `paired_seed` and `independent_seed` in the
  campaign record.
- Do not combine outputs from different seed policies in one summary without
  recording the policy change.

## Deterministic replay

For a replay, keep constant:

- Python and package versions;
- operating system and native runtime where possible;
- simulation configuration, timestep, duration, and seed;
- execution order and parallelism;
- input dataset and all source files;
- serialization and plotting configuration.

Compare semantic metrics first and artifact hashes second. Byte-identical
output may not be possible when timestamps, native floating-point operations,
rendering, browser output, or metadata are generated at runtime.

## Logging

Every run log should contain:

- experiment/condition identifier;
- seed and seed role;
- start/end time and status;
- configuration hash;
- git commit;
- Python and package versions;
- input/output paths and checksums;
- retry, resume, interruption, or failure events.

An absent seed is `UNKNOWN`, never an inferred value.

## Campaign seed management

Define the seed list in the campaign YAML before running. Keep the same seed
list for a paired baseline/condition comparison unless the protocol explicitly
requires independent seeds. When resuming, skip only artifacts whose manifest,
checksum, and status are all valid. A failed or partial artifact receives a
new attempt record rather than being silently marked complete.

## Scientific boundary

Seed consistency supports computational reproducibility. It does not prove
that a Disease Layer parameter has biological meaning, that a phenotype is
Parkinson disease, or that a result has clinical or therapeutic validity.
