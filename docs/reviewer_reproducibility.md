# Reviewer Questions: Reproducibility and Scientific Audit

This document lists questions a reviewer may ask. It intentionally does not
answer them; each answer should be supported by archived artifacts and a
declared protocol.

## Runtime and software

1. Which Python, FlyGym, MuJoCo, and native backend versions were used?
2. Does the runtime checker output from the reported run exist?
3. Can an independent operator install the same environment from the release?
4. Which operating-system, GPU-driver, or rendering differences can affect the
   result?
5. Which source commit produced the reported artifacts?
6. Were uncommitted source changes present during execution?

## Inputs and provenance

7. Where did each dataset originate, and how was it identified?
8. Are all rollout, metadata, manifest, and checksum files available?
9. Can every reported metric be traced to an exact input file hash?
10. Were any files repaired, excluded, overwritten, or regenerated?
11. Are the configuration and version records complete for every experiment?
12. How were interrupted and retried runs represented in the history?

## Randomness and determinism

13. Which random seeds were used, and where are they recorded?
14. Which comparisons use paired seeds and which use independent seeds?
15. What is guaranteed to be deterministic, and what is only expected to be
    numerically similar?
16. Were execution order and parallelism controlled?
17. How were timestamps, metadata, figure rendering, and serialization
    differences handled?
18. Can the reported semantic metrics be reproduced within declared
    tolerances?

## Calibration

19. Which literature records were manually approved before calibration?
20. Are target units, uncertainty, sample sizes, controls, and assay contexts
    documented?
21. How were calibration and holdout data separated?
22. Were parameter bounds and loss functions fixed before fitting?
23. Could the same target be used more than once through duplicated sources?
24. How were unavailable or incompatible metrics handled?

## Validation and statistics

25. What is the independent experimental unit: seed, rollout, animal, or
    another unit?
26. Which validation reference and comparison rule were used?
27. Were failed, missing, or outlier artifacts excluded, and why?
28. Which statistical method, resampling policy, and confidence interval were
    preregistered?
29. Can every figure and table be regenerated from archived input artifacts?
30. Are statistical conclusions being made beyond the available sample and
    evidence?

## Scientific interpretation

31. Which claims concern computational locomotion only?
32. What evidence would be required before describing a result as biological
    validation?
33. Does the Disease Layer represent a biological mechanism or a computational
    perturbation proxy?
34. Are diagnosis, clinical prediction, drug response, or therapeutic claims
    being made without external evidence?
35. What limitations remain because real datasets or wet-lab validation are
    absent?
