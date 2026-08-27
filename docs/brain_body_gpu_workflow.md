# Brain-Body GPU Workflow

Tài liệu này mô tả đường chạy tùy chọn dùng source brain-body ở ngoài repo
chính (`phase-A-clean`) với FlyGym/MuJoCo và các bộ xuất hiện có của repo này.
Đây là **computational locomotion simulation**. Nó không phải mô hình Parkinson
sinh học, chẩn đoán, dự đoán lâm sàng hay đánh giá thuốc.

## Phạm vi source

Repo chính cung cấp FlyGym body, recorder, rollout exporter, analysis,
biomarker và viewer exporter. Source `phase-A-clean` cung cấp:

- `brain_body_bridge.py` và `code/run_pytorch.py`;
- FlyWire v783 neuron table và connectivity parquet;
- checkpoint `data/plastic_weights.pt`.

Runner `scripts/run_brain_body_rollout.py` không đọc MP4 hoặc JSON summary để
tạo chuyển động. Nó thực sự gọi `BrainEngine.step()`, giải mã descending-neuron
rates, gửi action vào FlyGym/MuJoCo, rồi ghi từng frame bằng
`RolloutRecorder` của repo chính.

## Kiểm tra GPU

Trong PowerShell:

```powershell
nvidia-smi
```

Source brain cần một Python environment có PyTorch CUDA. Runner tự tìm theo thứ
tự:

1. `--brain-python` nếu được chỉ định;
2. `phase-A-clean/.venv/Scripts/python.exe` trên Windows;
3. `phase-A-clean/.venv/bin/python` trên Linux;
4. Python hiện tại.

Nếu Python hiện tại không có Torch/CUDA, runner tự khởi chạy lại bằng Python
của source brain. Không có bước tự cài package và không tự tải dữ liệu.

## Chạy baseline thật

Từ thư mục repo chính:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\run_brain_body_rollout.py `
  --condition healthy `
  --steps 1000 `
  --seed 0 `
  --device cuda `
  --output results\brain_body\healthy_seed_0
```

Log phải có các dòng tương tự:

```text
[BrainEngine] 138639 neurons on cuda
[BrainEngine] Hebbian plasticity active: 15091983 synapses
READY: ...\results\brain_body\healthy_seed_0
```

## Chạy condition computational

Condition này dùng cấu hình `configs/parkinson/computational_pd_like_demo.yaml`
và chỉ là các biến đổi action/controller đã có trong Disease Layer:

```powershell
python scripts\run_brain_body_rollout.py `
  --condition computational_pd_like_demo `
  --steps 1000 `
  --seed 0 `
  --device cuda `
  --compare-to results\brain_body\healthy_seed_0 `
  --output results\brain_body\computational_pd_like_demo_seed_0
```

`--compare-to` chỉ tạo bảng delta giữa metrics đã tính; nó không fit tham số
và không diễn giải delta là bằng chứng sinh học.

## Artifact

Mỗi run thành công tạo:

```text
results/brain_body/<run>/
├── rollout.json
├── rollout.npz
├── rollout.csv
├── viewer_pose.json
├── manifest.json
├── brain_body_summary.json
├── brain_body_manifest.json
├── metrics/
├── figures/
├── report/
├── biomarkers/
└── viewer_bundle.zip
```

`frame_count = steps + 1` vì frame khởi tạo cũng được ghi. Có thể xem pose
trực tiếp bằng server viewer hiện có:

```powershell
python scripts/run_viewer.py `
  --pose results\brain_body\healthy_seed_0\viewer_pose.json
```

Hoặc giải nén `viewer_bundle.zip` rồi mở `viewer_bundle/index.html` qua một
static HTTP server. Không mở `index.html` bằng `file://` nếu trình duyệt chặn
fetch JSON.

## Diễn giải đúng

`healthy` là baseline computational của controller/brain-body source. Một
condition có tên `computational_pd_like_demo` chỉ cho biết action-level
perturbation đã được áp dụng. Để gọi kết quả là concordant với literature cần
target số đã được nhóm nghiên cứu duyệt, nhiều seed, holdout độc lập và
provenance đầy đủ.

Nếu source `phase-A-clean` hoặc checkpoint không tồn tại, runner dừng với lỗi
rõ ràng. Không thể tái tạo frame-level movement từ các video đã render.
