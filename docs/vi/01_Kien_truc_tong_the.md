# 2. Kiến trúc tổng thể

## Sơ đồ chính

```text
FlyGym / Scene JSON
        ↓
   Rollout Loader
        ↓
   Validation + QC
        ↓
   Workspace / Experiment Workspace
        ↓
   Analysis + Statistics
        ↓
 Visualization + Reports
        ↓
       Export
        ↓
  Plugin Platform (extension boundary)
```

Plugin Platform là lớp mở rộng, không thay thế các bước hiện có. Plugin chỉ
nhận `PluginContext` và dữ liệu được host truyền vào. Context không chứa
đối tượng Workspace nội bộ.

## Các lớp web

- `workspace.js`: state của scene, selection, frame và playback.
- `experiment_workspace.js`: experiment, dataset, comparison, snapshot và
  registry legacy.
- `integration_workflow.js`: workflow import đến persistence.
- `analysis_pipeline.js`: feature graph, normalization, QC, outlier và cache.
- `statistical_engine.js`: thống kê mô tả, kiểm định, effect size, tương quan
  và report.
- `plugin_platform.js`: manifest, lifecycle, hook, capability, context và
  dependency checking.

## Tương thích

`ExperimentWorkspace.plugins` vẫn giữ `PluginRegistry` cũ. `pluginPlatform`
là API additive cho manifest-based plugin; hai API không bị trộn trạng thái.
