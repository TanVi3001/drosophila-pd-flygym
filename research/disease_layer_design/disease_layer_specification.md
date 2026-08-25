# Đặc tả khoa học Disease Layer

## 1. Mục đích

Disease Layer là lớp perturbation tính toán nằm giữa healthy controller và
action đưa vào FlyGym. Nó dùng để kiểm tra các giả thuyết về output vận động
trên dữ liệu mô phỏng đã được định nghĩa. Nó không phải biological Parkinson
model, neural connectome, dopamine simulation hoặc công cụ chẩn đoán.

Sprint 4 chỉ tạo đặc tả khoa học. Không thay đổi implementation, không chạy
simulation và không tạo calibration value.

## 2. Vị trí trong pipeline

```text
Healthy Controller
        |
        v
Disease Layer (computational proxies)
        |
        v
Action Modifier
        |
        v
FlyGym
        |
        v
Locomotion -> Metrics -> Evidence-constrained Calibration
```

Disease Layer nhận action/state của healthy controller, áp dụng proxy đã được
cấu hình, sau đó trả action hợp lệ cho simulation. Mỗi thay đổi phải được ghi
provenance: proxy, parameter, version, seed, protocol và dataset.

## 3. Quy tắc thiết kế

1. Healthy controller là baseline và không được thay đổi khi thiết kế proxy.
2. Proxy chỉ là computational interpretation của evidence, không phải cơ chế
   tế bào.
3. Không điền range số khi chưa có numeric literature target và uncertainty.
4. Không gộp các assay khác nhau chỉ vì cùng chứa từ `locomotion`.
5. Không coi evidence score là effect size hoặc biological importance.
6. Mapping nhiều proxy cho một metric phải được xem là confounding cần kiểm
   định, không phải causal graph đã chứng minh.
7. Chỉ dùng candidate đã được manual review và approved làm calibration target.

## 4. Proxy catalogue

| Proxy | Diễn giải tính toán | Coverage | Healthy default | Range Sprint 4 |
| --- | --- | --- | --- | --- |
| `motor_vigor` | Scale output vận động tổng thể | 15 paper; 0 quantitative | Giữ default hiện có | Chưa đề xuất |
| `coordination` | Điều chỉnh phối hợp action/joint/limb | 5 paper; 0 quantitative | Giữ default hiện có | Chưa đề xuất |
| `delay` | Trễ trước action/state transition | 0 paper | Không thêm delay | Chưa đề xuất |
| `noise` | Biến thiên thêm trong motor output | 1 paper; 0 quantitative | Giữ noise healthy | Chưa đề xuất |
| `fatigue` | Suy giảm theo thời gian | 0 paper | Không thêm fatigue | Chưa đề xuất |
| `latency` | Trễ phản hồi trong task | 1 paper; 0 quantitative | Giữ default hiện có | Chưa đề xuất |
| `asymmetry` | Sai khác có kiểm soát trái-phải | 0 paper | Giữ đối xứng healthy | Chưa đề xuất |
| `freezing` | Xác suất/thời lượng trạng thái đứng yên | 1 paper; 0 quantitative | Chưa bật freezing | Chưa đề xuất |
| `postural_instability` | Biến thiên ổn định tư thế thân/cánh | 6 paper; 0 quantitative | Giữ posture healthy | Chưa đề xuất |

Chi tiết đầy đủ của từng proxy, bao gồm biological motivation, affected
metrics, candidate và research gaps, nằm trong `proxy_design.csv` và
`proxy_design.json`.

## 5. Metric-proxy evidence

`metric_proxy_matrix.csv` là ma trận chuẩn hóa từ dependency matrix. Các liên
kết nổi bật:

- climbing -> motor_vigor: Strong, 8 paper và 10 mapping records.
- speed; trajectory -> motor_vigor: Strong, 1 paper.
- geotaxis -> motor_vigor: Strong, 1 paper.
- flight -> coordination: Moderate, 2 paper.
- posture -> postural_instability: Strong, 1 paper.
- idling -> freezing: Weak, 1 paper.
- time to finish -> latency: Weak, 1 paper.

Những liên kết trên chỉ cho biết evidence mapping hiện có. Chúng không xác
định hướng thay đổi, độ lớn thay đổi hay quan hệ nhân quả.

## 6. Parameter design

`parameter_design.csv` mô tả vai trò, hướng evidence-based và tương tác dự kiến.
`parameter_ranges.csv` cố ý để trống lower/upper bound cho cả 9 parameter.
Đây là trạng thái đúng: Evidence Engine báo 0 quantitative paper cho toàn bộ
proxy. Việc tự điền ví dụ như 0.8 hoặc 0.75 sẽ tạo calibration target không có
nguồn.

## 7. Trạng thái khoa học hiện tại

- `motor_vigor` là ưu tiên curation cao nhất theo coverage, không phải đã đủ
  để fit.
- `coordination` và `postural_instability` có candidate nhưng còn
  confounding và thiếu measurement trực tiếp.
- `noise`, `latency`, `freezing` chỉ có một mapping qualitative.
- `delay`, `fatigue`, `asymmetry` chưa có literature mapping.
- Không proxy nào được gắn nhãn diagnosis, clinical prediction hoặc biological
  confirmation.

## 8. Điều kiện chuyển sang calibration

Chỉ chuyển một metric-proxy link sang calibration khi:

- provenance của paper được xác minh;
- genotype, assay, age, sex, protocol và sample unit đã ghi rõ;
- outcome có value, unit và uncertainty hoặc lý do thiếu uncertainty;
- mapping đã được reviewer approve;
- metric mô phỏng có định nghĩa tương thích;
- calibration/holdout split được khóa trước khi fit.

