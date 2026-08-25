# Benchmark Acceptance Criteria

## Scientific scope

Các tiêu chí này kiểm tra rollout và artifact của **computational locomotion model**.
PASS không có nghĩa là biological Parkinson model, diagnostic model,
clinical prediction model, drug discovery model hay therapeutic validation.

## Healthy rollout PASS

Healthy rollout chỉ PASS khi tất cả điều kiện sau đây đều đạt:

- [ ] Runtime gate PASS.
- [ ] FlyGym/MuJoCo version và configuration được ghi.
- [ ] `rollout.json` tồn tại và đọc được.
- [ ] `rollout.npz` hoặc `rollout_arrays.npz` tồn tại và đọc được.
- [ ] `viewer_pose.json`, `manifest.json`, `metadata.json` tồn tại.
- [ ] Frame count đúng với expected steps và nhất quán giữa artifacts.
- [ ] Timestamps hữu hạn và strictly increasing sau khi áp dụng policy được ghi.
- [ ] Timestep dương và nhất quán trong tolerance đã định trước.
- [ ] Quaternion hữu hạn, non-zero và normalized sau khi load/validate.
- [ ] Thorax positions hữu hạn.
- [ ] Planar thorax displacement `> 0` theo benchmark requirement.
- [ ] Không có NaN trong observations hoặc derived metrics.
- [ ] Không có Inf trong observations hoặc derived metrics.
- [ ] Metrics report có source files, unit và channel availability.
- [ ] Checksum và manifest nhất quán.

Nếu thorax displacement bằng 0, rollout có thể có giá trị debug/contract riêng,
nhưng không được nhận là Healthy benchmark PASS theo tiêu chí Sprint này.

## Campaign PASS

Campaign chỉ PASS khi:

- [ ] Runtime gate PASS.
- [ ] Dataset gate PASS cho tất cả run được claim là completed.
- [ ] Đủ số seed theo benchmark matrix.
- [ ] Đủ số steps và duration theo condition.
- [ ] Parameter, proxy và condition ID được ghi trong manifest.
- [ ] Baseline được chạy cùng protocol với condition.
- [ ] Artifact đầy đủ cho từng condition.
- [ ] Checksum đúng và có thể verify lại.
- [ ] Manifest đúng, không trỏ tới file ngoài campaign mà không ghi rõ.
- [ ] Metrics finite và metric availability được báo cáo.
- [ ] Failed/waiting runs được tách khỏi completed summary.
- [ ] Log, config hash, git commit, seed và runtime metadata được lưu.
- [ ] Không có output được tạo bằng dữ liệu giả hoặc overwrite raw artifact.

## Metric acceptance

- [ ] Metric name khớp `docs/metric_definition.md`.
- [ ] Formula variant được ghi rõ nếu repository có nhiều implementation.
- [ ] Unit có mặt.
- [ ] Missing metric là `unavailable`, không phải 0.
- [ ] Denominator, threshold và window được lưu khi có.

## Statistical acceptance

- [ ] Unit of analysis và pairing được xác định.
- [ ] Số seed đủ cho phương pháp dự kiến.
- [ ] Không coi frames trong một rollout là independent replicates.
- [ ] Analysis plan được khóa trước khi xem kết quả.
- [ ] Multiplicity, CI và effect size policy được ghi.

## Release decision

- `PASS`: tất cả bắt buộc đạt và artifact có provenance.
- `FAILED`: đã chạy nhưng một acceptance criterion bắt buộc không đạt.
- `WAITING_RUNTIME`: runtime chưa sẵn sàng.
- `WAITING_DATASET`: dataset/artifact chưa đủ.
- `NOT_APPLICABLE`: proxy chưa implement hoặc metric không thuộc contract.

Không chuyển trạng thái bằng cách bỏ qua failure hoặc điền số liệu thiếu.
