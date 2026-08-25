# Experimental Benchmark Protocol

## 1. Phạm vi khoa học

Protocol này là chuẩn kiểm tra cho các rollout FlyGym trong tương lai. Nó mô
tả chất lượng dữ liệu, reproducibility, metric và artifact; không tạo benchmark
result trong task này.

Repository hiện cung cấp một **computational locomotion model** và các lớp
post-processing. Đây không phải biological Parkinson model, diagnostic model,
clinical prediction model, drug discovery model hay therapeutic validation.

## 2. Mục tiêu benchmark

- Xác nhận rollout có thể đọc, phân tích và tái lập.
- Đảm bảo Healthy baseline được dùng làm reference trước perturbation.
- Đo response của từng proxy bằng cùng metric, timestep, duration và protocol.
- Tách software/data integrity khỏi diễn giải khoa học.
- Tạo artifact đủ provenance cho calibration, validation và publication.

Benchmark không được dùng để tự gán mức độ bệnh, xác nhận cơ chế Parkinson hay
thay thế dữ liệu wet-lab.

## 3. Đối tượng áp dụng

Protocol áp dụng cho:

- Healthy baseline;
- Motor Vigor;
- Coordination;
- Noise;
- Delay;
- Fatigue;
- Asymmetry;
- Freezing;
- Latency;
- Postural Instability.

Proxy chưa implement runtime phải có trạng thái `NOT_IMPLEMENTED`, không được
thay thế bằng một proxy khác.

## 4. Điều kiện runtime

Trước mọi benchmark:

1. Python phải là 3.12.x.
2. FlyGym, MuJoCo và `flygym_demo` phải đạt `PASS` trong
   `python scripts/check_runtime.py`.
3. Phiên bản, git commit, operating system, CPU/GPU và package versions phải
   được lưu trong metadata.
4. GPU chỉ là yêu cầu vận hành tùy workload; GPU không thay thế runtime gate.

Nếu gate fail, trạng thái benchmark là `WAITING_RUNTIME`, không chạy
simulation và không tạo result giả.

## 5. Điều kiện dataset

Mỗi rollout benchmark phải có:

```text
<dataset_id>/
  rollout.json
  rollout.npz hoặc rollout_arrays.npz
  viewer_pose.json
  manifest.json
  metadata.json
  metrics/
  validation/
  logs/
```

Raw rollout phải giữ nguyên sau archive. Dataset phải vượt acceptance criteria:
finite values, timestamps hợp lệ, quaternion hợp lệ, frame count đúng, timestep
được ghi và thorax displacement dương theo protocol.

## 6. Thiết kế benchmark

- Chạy Healthy trước từng proxy.
- Mỗi condition chỉ thay một proxy trong single-proxy benchmark.
- Giữ controller, world, timestep, duration và observation contract cố định.
- Ghi rõ seed; không gộp các seed khác nhau thành một observation duy nhất.
- Dùng cùng window và metric definition khi so sánh baseline/condition.
- Multi-proxy interaction chỉ được mở sau khi single-proxy benchmark đã review.

Các giá trị trong `research/benchmark_matrix.csv` là kế hoạch kỹ thuật. Chúng
không phải range sinh học hoặc calibration target.

## 7. Quy trình thực thi

1. Runtime gate.
2. Healthy smoke rollout.
3. Dataset validation và checksum.
4. Healthy replicate benchmark.
5. Một proxy một lần, theo sweep đã khóa.
6. Phân tích metric và kiểm tra missing channels.
7. Cross-seed summary.
8. Validation và artifact review.
9. Chỉ sau đó mới chuẩn bị calibration/statistical analysis.

Một condition lỗi phải giữ log và chuyển `FAILED`; không âm thầm bỏ qua hoặc
ghi đè bằng output mới.

## 8. Statistical requirement

Không chạy thống kê nếu chưa đủ số seed, không có unit, hoặc các run không cùng
protocol. Trước khi chọn test phải kiểm tra independent/paired structure,
repeated seeds, missingness, outliers, distribution và batch effects. Chi tiết
được ghi trong [`statistical_analysis_plan.md`](statistical_analysis_plan.md).

## 9. Reproducibility requirement

Mỗi condition phải lưu:

- condition ID và proxy parameter;
- seed;
- số steps, timestep, duration;
- config và config hash;
- git commit và runtime versions;
- source dataset và checksum;
- output manifest, checksum và execution log.

Một lần chạy lại phải có thể xác định được khác biệt do code, environment,
seed, hardware hoặc nondeterminism. Không gọi là reproducible nếu chỉ có
`metrics.csv` mà không có raw provenance.

## 10. Expected artifacts

Mỗi benchmark campaign nên có:

```text
results/<campaign>/
  campaign_status.json
  experiment_summary.md
  response_surface.csv/json
  parameter_sensitivity.csv/json
  validation/
  logs/
```

Các artifact chỉ được đưa vào paper package sau khi acceptance criteria và
checksum PASS.

## 11. Scientific boundary

Benchmark chỉ đánh giá computational locomotion response và software/data
integrity. Nó không chứng minh biological concordance, chẩn đoán Parkinson,
clinical prediction, drug response hoặc therapeutic efficacy.

