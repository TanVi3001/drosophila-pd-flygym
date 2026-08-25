# Kế hoạch quản lý dữ liệu

## Nguyên tắc

- Chỉ lưu dữ liệu do runtime FlyGym thực sự tạo hoặc literature có provenance.
- Không tạo rollout giả, không thay giá trị thiếu bằng số 0 và không ghi đè raw
  artifact đã được archive.
- Raw data, derived analysis và publication asset phải tách biệt.
- Artifact quan trọng phải có manifest, checksum, seed, cấu hình và phiên bản
  runtime.

## Cấu trúc workspace

```text
datasets/
  healthy/Healthy_001/
  pd_mild/PD_Mild_001/
  pd_moderate/PD_Moderate_001/
  pd_severe/PD_Severe_001/
results/
logs/
cache/
temporary/
backup/
paper/
```

`datasets/` chứa rollout và metadata gốc. `results/` chứa output dẫn xuất.
`logs/` chứa log chạy. `cache/` chỉ chứa dữ liệu tái tạo được. `temporary/`
chỉ dùng trong một job và phải dọn sau khi artifact đã commit nguyên tử.
`backup/` nằm trên storage khác với workspace chạy.

## Dataset layout và naming

Mỗi dataset thật nên có tối thiểu:

```text
Healthy_001/
  rollout.json
  rollout.npz hoặc rollout_arrays.npz
  viewer_pose.json
  manifest.json
  metadata.json
  metrics/
  biomarkers/
  validation/
  reports/
  figures/
  logs/
```

Tên dùng chữ, số và dấu gạch dưới; ID ổn định và không tái sử dụng cho dataset
khác. Condition/seed nên ghi trong metadata thay vì nhúng thông tin không nhất
quán vào tên file.

## Metadata bắt buộc

Mỗi run ghi: dataset ID, experiment ID, condition, seed, git commit, Python
version, FlyGym/MuJoCo version, config path/hash, timestep, số bước, thời gian
chạy, hostname/GPU (nếu có), thời điểm bắt đầu/kết thúc và nguồn dữ liệu. Nếu
field không có, ghi rõ `unavailable`.

## Manifest và checksum

Manifest liệt kê file thuộc artifact, kích thước và vai trò. Checksum SHA-256
được tạo sau khi file hoàn tất, không trong lúc file còn đang ghi. Sau khi copy
hoặc giải nén, kiểm tra checksum và manifest consistency trước khi analysis.

Không sửa rollout JSON, NPZ hoặc viewer pose sau khi đã ghi nhận là raw. Nếu
cần xử lý, tạo thư mục derived mới và liên kết tới raw input.

## Quy trình lưu an toàn

1. Ghi vào `temporary/<run-id>`.
2. Kiểm tra file bắt buộc, JSON/NPZ đọc được và frame count.
3. Tạo manifest và checksum.
4. Move cả thư mục sang vị trí chính thức sau khi kiểm tra thành công.
5. Ghi log và registry.
6. Copy backup và xác minh checksum ở backup.

Nếu job bị ngắt, không coi temporary là dataset hợp lệ. Giữ log lỗi để điều
tra rồi resume bằng run ID mới hoặc policy đã được review.

## Retention và backup

- Giữ raw rollout và metadata trong suốt vòng đời nghiên cứu.
- Giữ derived metrics, validation và report cùng raw checksum.
- Có ít nhất hai bản backup độc lập trước khi xóa temporary/cached data.
- Không commit file lớn như NPZ, video, zip hoặc raw rollout vào Git nếu policy
  repository không cho phép.
- Trước khi upload publication artifact, tạo manifest cấp campaign.

## Kiểm soát chất lượng

Dataset chỉ chuyển sang `READY` sau runtime/dataset validation PASS. Dataset
thiếu file, checksum mismatch, NaN/Inf hoặc timestamp/quaternion lỗi phải ở
trạng thái INVALID/FAILED. Chênh lệch giữa các run chỉ được báo cáo, không tự
giải thích sinh học.

## Trạng thái hiện tại

Task này không tạo dataset. Nhóm cần tạo Healthy_001 trong runtime Python 3.12
với FlyGym/MuJoCo hợp lệ trước khi mở rộng campaign.

