# Reproducibility Levels

These levels are definitions for future audit reports. They are not scores and
this document does not assign a level to the repository.

## Level A - Traceable record

The artifact has an identifier, producer, input/output paths, configuration,
version metadata, seed policy where relevant, and a written provenance record.
The result can be inspected, but a complete rerun may not yet be possible.

## Level B - Verifiable artifact

Level A requirements are met, and the artifact has a valid manifest,
checksums, schema/format information, and integrity checks. A reviewer can
verify that the stored files match the declared record.

## Level C - Computationally replayable

Level B requirements are met, and an independent operator can rerun the
declared workflow from the pinned source, runtime, inputs, configuration, and
seeds. Semantic outputs and documented tolerances can be compared. Byte
identity is required only where the producer explicitly guarantees it.

## Level D - Independently corroborated

Level C requirements are met, and an independent environment, dataset split,
or external reference can corroborate the reported computational result under
the preregistered protocol. The evidence, deviations, and limitations are
archived.

Level D still does not mean biological validation, clinical validity, or
therapeutic efficacy. Those claims require evidence outside this computational
repository.
