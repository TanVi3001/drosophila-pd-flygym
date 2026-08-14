# 4. Các module

| Module | Nhiệm vụ | Input | Output / phụ thuộc |
|---|---|---|---|
| `flygym_rollout.js` | Nhận dạng và chuẩn hóa rollout FlyGym | JSON rollout | rollout chuẩn hóa |
| `analysis_pipeline.js` | Chạy graph, normalization, QC và cache | rollout | analysis report |
| `statistical_engine.js` | Tính thống kê và tạo report | feature/value arrays | statistics/report |
| `integration_workflow.js` | Nối import đến persistence | rollout | workflow result |
| `experiment_workspace.js` | Quản lý experiment, dataset và snapshot | rollout/metadata | workspace state |
| `plugin_platform.js` | Lifecycle, manifest, hook và capability | plugin definition | plugin result/hook result |
| `verification_suite.js` | Kiểm chứng workflow và benchmark | rollout thật | verification report |
| `parkinson_export.js` | Export phân tích | analysis data | JSON/CSV/Markdown/HTML/SVG |

## Plugin examples

- `web/plugins/analysis_plugin.js`
- `web/plugins/statistics_plugin.js`
- `web/plugins/export_plugin.js`

Đây là extension boundary và ví dụ API, không phải kết quả khoa học mới.
