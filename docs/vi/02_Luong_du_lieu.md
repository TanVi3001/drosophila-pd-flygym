# 3. Luồng dữ liệu

```text
Input
  ↓
Validation
  ↓
Normalization
  ↓
Quality Control
  ↓
Feature Extraction
  ↓
Analysis
  ↓
Statistics
  ↓
Visualization
  ↓
Reports
  ↓
Export
```

## Plugin hook

Plugin có thể đăng ký hook cho các điểm mở rộng sau:

`onImport`, `onValidation`, `onNormalization`, `onQC`,
`onFeatureExtraction`, `onAnalysis`, `onStatistics`, `onComparison`,
`onVisualization`, `onReport`, `onExport`, `onWorkspaceLoaded`.

Host quyết định payload nào được gửi. Hook không được tự ý đọc Workspace
nội bộ và không được thay đổi frozen evidence.

## Xử lý lỗi

Loader phải validate manifest trước khi load. Nếu dependency thiếu hoặc hook
không hợp lệ, plugin bị từ chối. Khi import rollout thất bại, workflow hiện có
rollback workspace; plugin không được bypass cơ chế đó.
