# SOP chạy thí nghiệm trên server

## Mục tiêu

SOP này mô tả cách nhóm nghiên cứu chạy runtime FlyGym thật và lưu artifact có
thể tái lập. Không chạy nếu runtime gate chưa PASS. Không tạo dữ liệu thay thế
khi package hoặc dataset thiếu.

## 1. Chuẩn bị server

1. Chọn thư mục workspace trên persistent volume.
2. Kiểm tra dung lượng và quyền ghi.
3. Nếu dùng GPU, chạy `nvidia-smi` và lưu thông tin GPU vào log job.
4. Clone đúng commit/tag đã được phê duyệt.
5. Không chạy đồng thời nhiều job vào cùng output directory.

Ví dụ Linux:

```bash
git clone <repository-url>
cd drosophila-pd-flygym
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[simulation,test]"
```

Trên Windows PowerShell, dùng `py -3.12 -m venv .venv` và
`.venv\Scripts\Activate.ps1`. Việc cài đặt phải tuân chính sách server; SOP
không tự cài package khi chạy experiment.

## 2. Runtime gate

```bash
python scripts/check_runtime.py
```

Nếu dependency bắt buộc FAIL, dừng. Ghi `WAITING_RUNTIME`, lỗi đầy đủ và phiên
bản hiện có. Không chạy `run_demo.py`, không tạo dataset rỗng và không đánh dấu
campaign là failed scientific result.

## 3. Healthy smoke run

```bash
python scripts/run_demo.py --steps 100
```

Sau khi lệnh kết thúc, xác nhận bằng filesystem và validation:

```bash
python scripts/validate_research_workflow.py \
  --dataset datasets/healthy/Healthy_001 \
  --output results/validation/Healthy_001
```

Không archive nếu thiếu rollout JSON/NPZ, viewer pose, manifest, metadata,
hoặc nếu validation không PASS.

## 4. Phân tích Healthy_001

```bash
python scripts/analyze_rollout.py \
  --dataset datasets/healthy/Healthy_001 \
  --output results/analysis/Healthy_001

python scripts/analyze_computational_pd.py \
  --input datasets/healthy/Healthy_001/rollout.json \
  --output results/biomarkers/Healthy_001
```

Kiểm tra frame count, timestep, duration, finite values và các metric thực sự
có trong report. Field thiếu phải ghi `unavailable`.

## 5. Chạy campaign

Trước khi chạy phải có campaign YAML đã review, seed list, approved numeric
targets và backup Healthy_001.

```bash
python scripts/run_experimental_campaign.py \
  --campaign configs/experiments/campaign_v1.yaml
```

Nếu nhận `WAITING_TARGET_DATA`, dừng đúng tại đó. Không sửa template bằng số
ước đoán và không bypass gate. Với nhiều rollout đã có, chạy experiment suite:

```bash
python scripts/run_experiment_suite.py \
  --config-dir experiments \
  --output results/experiments
```

## 6. Validation và concordance

Sau campaign, kiểm tra response surface, seed count và checksum. Chỉ khi có
`campaign_data.json` và simulation metrics mới chạy:

```bash
python scripts/run_concordance_analysis.py
```

`WAITING_SIMULATION` là trạng thái hợp lệ khi chưa có simulation; không đổi nó
thành PASS bằng cách tạo file thủ công.

## 7. Viewer và archive

```bash
python scripts/build_viewer_bundle.py \
  --pose datasets/healthy/Healthy_001/viewer_pose.json \
  --output dist/viewer_bundle.zip
```

Mở bundle bằng static server phù hợp, kiểm tra pose đúng dataset, rồi lưu zip,
manifest, checksum và log vào backup. Không dùng viewer pose cũ từ run khác.

## 8. Quy tắc khi job bị ngắt

1. Không xóa output để “chạy cho sạch”.
2. Lưu stdout/stderr và trạng thái process.
3. Đánh dấu run là interrupted/failed trong execution log.
4. Kiểm tra file tạm và checksum trước khi resume.
5. Resume vào run ID/output directory mới nếu policy chưa cho phép tiếp tục
   nguyên tử.
6. Chỉ ghép kết quả sau khi mỗi condition đã qua validation.

## 9. Backup và bàn giao

Mỗi bàn giao gồm:

- git commit/tag;
- runtime matrix;
- config và config hash;
- seed list;
- dataset/condition inventory;
- manifest/checksum;
- metrics, validation, report;
- viewer bundle nếu có;
- execution log và incident note nếu có lỗi.

Bên nhận phải kiểm tra checksum trước khi phân tích hoặc xuất bản.

## 10. Giới hạn SOP

SOP không chạy song song, không cài dependency tự động và không thêm proxy
scientific. Nếu cần scheduler, retry policy nâng cao hoặc proxy mới, ghi
`Future software improvement` và thực hiện review riêng, không sửa SOP để bỏ
qua gate.

