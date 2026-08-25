# Kế hoạch thực thi runtime

## Phạm vi

Tài liệu này là kế hoạch vận hành, không phải kết quả thí nghiệm. Không có
simulation, dataset, figure hoặc kết luận sinh học nào được tạo trong task này.
Mọi bước chỉ được chạy sau khi bước gate trước đó trả về `PASS`.

## Điều kiện runtime

| Thành phần | Yêu cầu | Trạng thái audit hiện tại |
| --- | --- | --- |
| Python | 3.12.x | `WAITING_RUNTIME`: môi trường hiện tại là 3.13.x |
| FlyGym | 2.1.0 theo runtime matrix | Chưa khả dụng trong môi trường audit |
| MuJoCo | 3.9.0 theo runtime matrix | Chưa khả dụng trong môi trường audit |
| `flygym_demo` | Có thể import | Chưa khả dụng trong môi trường audit |
| NumPy, Matplotlib, PyYAML | Có thể import | Đã kiểm tra ở môi trường hiện tại |
| GPU | Khuyến nghị cho server lớn | Chưa được xác minh trong audit |

`scripts/check_runtime.py` chỉ kiểm tra và báo cáo; không tự cài đặt runtime.

## Thứ tự chạy có kiểm soát

### 1. Runtime gate

```bash
python scripts/check_runtime.py
```

Chỉ tiếp tục khi Python, FlyGym, MuJoCo và `flygym_demo` đều đạt yêu cầu. Nếu
không, dừng với `WAITING_RUNTIME` và giữ nguyên workspace.

### 2. Smoke test Healthy

```bash
python scripts/run_demo.py --steps 100
```

`run_demo.py` dùng pipeline FlyGym hiện có và tạo dataset mặc định dưới
`datasets/healthy/Healthy_001` cùng artifact viewer cần thiết.

Kiểm tra tối thiểu:

```text
datasets/healthy/Healthy_001/rollout.json
datasets/healthy/Healthy_001/rollout.npz hoặc rollout_arrays.npz
datasets/healthy/Healthy_001/viewer_pose.json
datasets/healthy/Healthy_001/manifest.json
datasets/healthy/Healthy_001/metadata.json
```

### 3. Dataset validation

```bash
python scripts/validate_research_workflow.py \
  --dataset datasets/healthy/Healthy_001 \
  --output results/validation/Healthy_001
```

Chỉ tiếp tục nếu validation trả `PASS`. Dataset lỗi phải được giữ lại cùng
log để điều tra, không bị ghi đè.

### 4. Phân tích rollout

```bash
python scripts/analyze_rollout.py \
  --dataset datasets/healthy/Healthy_001 \
  --output results/analysis/Healthy_001
```

Đây là phân tích read-only trên rollout đã nhập; output gồm metrics, summary
và dashboard của module analysis hiện có.

### 5. Computational PD/biomarker report

```bash
python scripts/analyze_computational_pd.py \
  --input datasets/healthy/Healthy_001/rollout.json \
  --output results/biomarkers/Healthy_001
```

Báo cáo này chỉ là computational phenotype/biomarker output. Nó không phải
chẩn đoán, dự đoán lâm sàng hay xác nhận bệnh học.

### 6. Experiment suite

Chỉ chạy sau khi có dataset thật và cấu hình đã được review:

```bash
python scripts/run_experiment_suite.py \
  --config-dir experiments \
  --output results/experiments
```

### 7. Experimental campaign

```bash
python scripts/run_experimental_campaign.py \
  --campaign configs/experiments/campaign_v1.yaml
```

Campaign có runtime gate và approved numeric target gate. Với
`research/campaign/calibration_targets.csv` còn là template rỗng, trạng thái
dự kiến là `WAITING_TARGET_DATA`, không sinh response surface.

### 8. Concordance analysis

```bash
python scripts/run_concordance_analysis.py
```

Chỉ chạy sau khi campaign có `campaign_data.json` và simulation metrics. Khi
chưa có simulation, output hợp lệ là `WAITING_SIMULATION`.

### 9. Viewer bundle

```bash
python scripts/build_viewer_bundle.py \
  --pose datasets/healthy/Healthy_001/viewer_pose.json \
  --output dist/viewer_bundle.zip
```

Bundle chỉ đóng gói artifact thật và web viewer hiện có.

### 10. Archive và reproducibility record

Cuối mỗi lần chạy, lưu git commit, cấu hình YAML, seed, phiên bản runtime,
manifest, checksum, log và thời điểm chạy. Chỉ archive thư mục đã qua
validation.

## Bảng input/output

| Bước | Input chính | Output cần kiểm tra |
| --- | --- | --- |
| Runtime check | Python và package environment | Runtime status |
| Smoke simulation | Healthy config, seed, FlyGym | rollout, metadata, manifest |
| Validation | Dataset directory | validation report |
| Analysis | rollout JSON/NPZ | metrics, summary, dashboard |
| Biomarker/PD report | Rollout và metric hiện có | computational report |
| Experiment suite | Experiment YAML và dataset thật | summary, reports, figures |
| Campaign | Campaign YAML, approved targets | response surface và status |
| Concordance | Evidence, design, campaign data | agreement và limitations |
| Viewer bundle | viewer pose và `web/` | `dist/viewer_bundle.zip` |

## Ước lượng vận hành

Các con số dưới đây là **quota lập kế hoạch**, chưa phải benchmark của máy
chạy thật:

- Một smoke rollout 100 bước: thường từ vài giây đến vài phút tùy runtime;
  cần đo lại bằng log thực tế.
- Một campaign 5 seed và 5 mức tham số: có thể từ vài phút đến vài giờ;
  không dùng ước lượng này làm kết quả hiệu năng.
- Nên dành ít nhất 1 GB trống cho smoke và 10--20 GB cho chiến dịch nhiều
  dataset kèm log/backup. Dung lượng thật phải ghi sau Healthy_001.

## Điều kiện dừng

Dừng ngay khi gặp `WAITING_RUNTIME`, `WAITING_DATASET`,
`WAITING_TARGET_DATA`, validation failure hoặc artifact thiếu. Giữ log và
manifest của lần chạy; không xóa để làm báo cáo có vẻ hoàn chỉnh.

