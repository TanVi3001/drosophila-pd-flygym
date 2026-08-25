# Kế hoạch Experimental Campaign

## Mục đích và phạm vi

Campaign này khảo sát cách các tham số perturbation tính toán ảnh hưởng tới
locomotion metrics. Đây là kế hoạch chạy thử nghiệm, không phải kết quả và
không phải mô hình sinh học Parkinson đã được xác nhận.

Mỗi campaign phải dùng rollout do FlyGym tạo ra, seed được ghi lại, và chỉ
được chạy sau runtime gate, dataset gate và review protocol.

## Các campaign đề xuất

| Campaign | Parameter values dự kiến | Seeds | Steps | Mục đích |
| --- | --- | ---: | ---: | --- |
| 0. Healthy baseline | giá trị healthy mặc định | 5 | 5.000 | Kiểm tra ổn định và tái lập baseline |
| 1. Motor vigor | 1.00, 0.95, 0.90, 0.85, 0.80 | 5 | 5.000 | Response của motor output scale |
| 2. Coordination | 1.00, 0.90, 0.80, 0.70, 0.60 | 5 | 5.000 | Response của CPG coupling scale |
| 3. Noise | 0.00, 0.01, 0.05* | 5 | 5.000 | Action noise nếu cấu hình được review |
| 4. Delay | 0, 5, 10* bước | 5 | 5.000 | Initiation delay |
| 5. Fatigue | 0.00, 0.01, 0.05* | 5 | 5.000 | Action decay theo thời gian |
| 6. Latency | Chưa đề xuất | - | - | Chưa có proxy/state chạy được |
| 7. Freezing | Chưa đề xuất | - | - | Chưa có state freezing chạy được |
| 8. Asymmetry | Chưa khóa giá trị | - | - | Chờ xác minh left/right joint mapping |
| 9. Postural instability | Chưa đề xuất | - | - | Chưa có proxy postural riêng |

Giá trị có dấu `*` là điểm khảo sát kỹ thuật cần review; không phải range sinh
học, target literature hay mức độ bệnh.

## Quy mô dự kiến

Nếu chạy campaign 0--5 với số điểm trong bảng, tổng là 100 lần chạy
điều kiện/seed (5 + 25 + 25 + 15 + 15 + 15). Đây là số lần thực thi dự kiến,
không phải 100 dataset sinh học độc lập. Có thể giảm quy mô sau smoke test để
đo thời gian và dung lượng thực tế.

## Thứ tự thực thi

1. Healthy baseline với 5 seed.
2. Kiểm tra repeatability, frame count, timestep và artifact integrity.
3. Motor vigor sweep đơn proxy.
4. Coordination sweep đơn proxy.
5. Noise, delay và fatigue chỉ sau khi hai sweep đầu đạt quality gate.
6. Chỉ xem xét tương tác nhiều proxy sau khi response curve đơn proxy đã review.
7. Không đưa latency, freezing hoặc postural instability vào campaign cho tới
   khi implementation và metric tương ứng được phê duyệt.

## Metric cần thu thập

Ưu tiên metric đã có: planar displacement, path length, mean planar speed,
heading yaw change/variance nếu có, trajectory efficiency, sample/step count,
timestep, duration, finite checks và metric joint/COM/orientation chỉ khi
artifact thực tế cung cấp.

Metric không có phải ghi `unavailable`, không điền 0. Mọi response surface phải
ghi mean, độ phân tán phù hợp, số seed và artifact nguồn.

## Gate và điều kiện dừng

- Runtime không PASS: `WAITING_RUNTIME`, không chạy simulation.
- Không có dataset/rollout thật: `WAITING_DATASET`, không sinh output khoa học.
- Không có approved numeric targets: `WAITING_TARGET_DATA`, không calibration.
- Validation hoặc manifest lỗi: dừng condition, giữ log và chuyển FAILED.
- Có NaN/Inf, quaternion không hợp lệ hoặc timestep lỗi: dừng trước analysis.
- Không diễn giải chênh lệch metric thành kết luận Parkinson.

## Sản phẩm dự kiến sau khi chạy

Output campaign v1 gồm response surface, sensitivity ranking, campaign summary
và campaign status trong `results/experimental_campaign/`. Chỉ output tạo từ
simulation thật mới được đưa vào phân tích tiếp theo.

## Phần chưa triển khai

Latency, freezing và postural instability là khoảng trống implementation,
không phải campaign đang chờ chạy. Việc bổ sung chúng là **Future software
improvement** và nằm ngoài kế hoạch vận hành này.

