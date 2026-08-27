# External Artifact Audit

- Archive: `drosophila_pd_all_videos.zip`
- SHA256: `83e6d7dfda9656d29aa612bc6fe11e5b6d04e926af7cf82cd2e35fef43913bd3`
- Status: **PARSEABLE_DERIVED_ARTIFACTS**

## Inventory

- Members: 15
- JSON: 7
- Video: 8
- Other: 0
- Raw rollout files: 0
- Viewer pose files: 0

## JSON Reports

| File | Model | Status | Overall pass | Samples | Speed (baseline -> perturbed) |
| --- | --- | --- | --- | ---: | ---: |
| `pink1_parkin_OE_age25_locomotion.json` | `pink1_parkin_OE_age25` | PARSED | True | 5001 | 12.568372100573873 -> 11.981251355628846 |
| `pink1_locomotion.json` | `pink1` | PARSED | True | 5001 | 12.568372100573873 -> 14.410521353596543 |
| `complexI_locomotion.json` | `complexI` | PARSED | True | 5001 | 12.568372100573873 -> 13.979692961939309 |
| `parkin_locomotion.json` | `parkin` | PARSED | True | 5001 | 12.568372100573873 -> 11.98666862250425 |
| `lrrk2_locomotion.json` | `lrrk2` | PARSED | True | 5001 | 12.568372100573873 -> 14.283457719970892 |
| `dj1_locomotion.json` | `dj1` | PARSED | True | 5001 | 12.568372100573873 -> 11.918868570297617 |
| `pink1_age25_locomotion.json` | `pink1_age25` | PARSED | True | 5001 | 12.568372100573873 -> 10.682772228544117 |

## Provenance and Scope

- Video bytes were inventoried and hashed but not decoded by this tool.
- The archive contains derived reports and videos, not `rollout.json`, `rollout.npz`, or `viewer_pose.json`.
- JSON fields referencing an external `bridge_scales`/`fly-brain` source are unresolved against this repository.
- The reports do not provide a source git commit (`git_commit` is null); reproducibility is therefore incomplete.
- The files must not be presented as raw biological recordings or as biological validation.

### Unresolved references

- `bridge_scales.json from fly-brain brain_body_bridge.py`
- `data/bridge_scales/complexI_bridge_scales.json`
- `data/bridge_scales/dj1_bridge_scales.json`
- `data/bridge_scales/lrrk2_bridge_scales.json`
- `data/bridge_scales/parkin_bridge_scales.json`
- `data/bridge_scales/pink1_age25_bridge_scales.json`
- `data/bridge_scales/pink1_bridge_scales.json`
- `data/bridge_scales/pink1_parkin_OE_age25_bridge_scales.json`

## Next evidence required

1. Preserve the source commit and exact runtime manifest for every report.
2. Supply the raw rollout and viewer-pose artifacts when a viewer or metric audit is required.
3. Link each video to an explicit condition/seed record; do not infer pairings from filenames.
4. Review the literature mappings manually before using any value as a calibration target.
