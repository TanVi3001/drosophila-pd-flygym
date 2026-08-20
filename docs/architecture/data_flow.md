# Data Flow

    FlyGym + MuJoCo
          |
          v
    RolloutRecorder -- observations --> rollout.json / rollout.npz
          |                                      |
          |                                      +--> viewer_pose.json --> web viewer
          v
    Imported rollout
          |
          +--> analysis metrics --> metrics and figures
          |
          +--> biomarker summaries --> reports
          |
          +--> experiment/research orchestration --> validation/publication assets

Every derived artifact should retain enough metadata to identify its source
dataset, configuration, software version, and generation status. Missing input
is a state such as WAITING_RUNTIME or WAITING_DATASET, not a reason to
fabricate a replacement.

## Review points

- Check the rollout manifest immediately after export.
- Check viewer-pose validity before building a viewer bundle.
- Check analysis input availability before reading metrics.
- Check validation status before publication packaging.
- Keep generated artifacts outside source modules and preserve the manifest.
