# Thiết kế validation

## 1. Mục tiêu

Validation kiểm tra liệu một Disease Layer configuration đã fit có tái tạo
được các target đã giữ lại hay không, trong phạm vi locomotion mô phỏng. Nó
không xác nhận bệnh sinh, chẩn đoán hoặc giá trị lâm sàng.

## 2. Các lớp validation

### 2.1 Software và artifact validation

- configuration parse được;
- parameter có provenance và version;
- rollout có frame, timestamp và quaternion hợp lệ;
- metrics finite và có manifest;
- output không ghi đè artifact ngoài experiment;
- hash và metadata nhất quán.

### 2.2 Healthy baseline validation

Chạy healthy controller với cùng protocol, seed policy và thời lượng như
condition. Baseline phải được lưu riêng để không nhầm với target disease.

### 2.3 Metric compatibility validation

Với từng metric, kiểm tra unit, sample unit, assay, developmental stage và
aggregation. Các metric không tương thích phải được đánh dấu `not_comparable`,
không ép vào một bảng tổng hợp.

### 2.4 Evidence holdout validation

Paper/target dùng để kiểm tra phải được khóa trước khi calibration. Không dùng
cùng một outcome để vừa fit vừa tuyên bố validation thành công.

### 2.5 Robustness và sensitivity

Đánh giá thay đổi kết quả khi:

- thay seed trong phạm vi protocol;
- thay replicate;
- bỏ một target;
- thay trọng số target đã được phê duyệt;
- dùng single-proxy so với multi-proxy.

Mọi phân tích phải báo cáo điều kiện chạy, không che giấu failure.

## 3. Validation candidates theo evidence hiện tại

| Proxy | Candidate metric | Trạng thái |
| --- | --- | --- |
| `motor_vigor` | climbing, flight, geotaxis, locomotion, speed/trajectory | Cần numeric extraction và approval |
| `coordination` | flight, crawling, climbing, angular change, locomotion | Cần metric coordination trực tiếp hơn |
| `noise` | AIM score; angular change | Chỉ treatment context; cần protocol |
| `latency` | time to finish | Chưa tách latency khỏi confounders |
| `freezing` | idling | Cần pause threshold/episode duration |
| `postural_instability` | climbing, flight, morphology, posture | Cần time-resolved posture/orientation |
| `delay`, `fatigue`, `asymmetry` | Không có | Chưa có literature mapping |

## 4. Failure criteria

Validation phải thất bại hoặc chuyển `not_ready` khi:

- target thiếu provenance hoặc unit;
- metric mô phỏng và literature không cùng định nghĩa;
- output có NaN/Inf hoặc artifact thiếu;
- kết quả chỉ đúng trên calibration set nhưng không kiểm tra được holdout;
- parameter không identifiable do confounding;
- diễn giải vượt quá phạm vi computational model.

Failure là kết quả hợp lệ của quy trình và phải được lưu cùng nguyên nhân.

## 5. Báo cáo bắt buộc

Mỗi validation run cần có:

- configuration và version;
- source target list;
- baseline condition;
- metric-level comparison;
- replicate/seed policy;
- missingness và exclusions;
- holdout result;
- limitation và unresolved gaps.

Không sinh kết luận khoa học nếu các điều kiện trên chưa đủ.

