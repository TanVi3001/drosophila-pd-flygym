# Calibration Priority

## Cách hiểu priority

Priority dưới đây là thứ tự chuẩn bị và vận hành, không phải xếp hạng mức độ
quan trọng của gene, bệnh hay cơ chế sinh học. Mục tiêu là giảm rủi ro kỹ thuật
và kiểm tra từng proxy một cách truy xuất được.

Mô hình vẫn chỉ là **computational locomotion model**. Nó không phải biological
Parkinson model, diagnostic model, clinical prediction model, drug discovery
model hay therapeutic validation.

## Thứ tự ưu tiên

| Priority | Proxy/step | Vì sao | Literature | Simulation/code | Calibration gate | Kết luận readiness |
| ---: | --- | --- | --- | --- | --- | --- |
| 0 | Healthy baseline | Cần identity reference trước mọi perturbation | Không phải disease evidence | Baseline runner có | Runtime + Healthy dataset | Bắt buộc trước tất cả proxy |
| 1 | `motor_vigor` | Đã có implementation và campaign path rõ nhất | 15 paper, qualitative-only | Có, campaign v1 bật | Chưa có numeric target | Ưu tiên chạy response characterization trước; chưa fit |
| 2 | `coordination` | Có implementation và liên quan contact/gait metrics | 5 paper, qualitative-only | Có, campaign v1 bật | Chưa có standardized target | Ưu tiên thứ hai; chưa fit |
| 3 | `noise` | Có field runtime nhưng chưa bật | 1 paper, qualitative-only | Có `motor_noise_std` | Cần target variance và seed protocol | Sensitivity sau motor/coordination |
| 4 | `delay` | Có field runtime, dễ tách thành single-proxy sweep | Không có paper trong coverage | Có `initiation_delay_steps` | Cần episode/timing target | Technical characterization, chưa calibration |
| 5 | `fatigue` | Có field nhưng cần rollout dài | Không có paper trong coverage | Có `fatigue_rate` | Cần longitudinal target | Chỉ sau khi duration protocol được khóa |
| 6 | `asymmetry` | Có tham số nhưng phụ thuộc mapping trái/phải | Không có paper trong coverage | Chưa an toàn; mapping rỗng trong campaign | Cần side mapping và target | Chờ validation contract |
| 7 | `freezing` | Cần state machine và operational assay | 1 paper, qualitative-only | Chưa implement runtime | Chưa có target | Chưa thể chạy |
| 8 | `latency` | Chưa có action-buffer implementation | 1 paper, qualitative-only | Chưa implement runtime | Chưa có target | Chưa thể chạy |
| 9 | `postural_instability` | Cần stabilizer và COM/orientation contract | 6 paper, qualitative-only | Chưa implement runtime | Chưa có target | Chưa thể chạy |

## Lý do không calibration ngay

Evidence Engine hiện ghi nhận `quantitative_paper_count = 0` cho toàn bộ proxy
trong coverage report. `parameter_ranges.csv` đánh dấu toàn bộ
`NOT_PROPOSED`, còn `calibration_targets.csv` chưa có dòng dữ liệu. Vì vậy
chạy sweep sau khi runtime sẵn sàng có thể là **response characterization**,
nhưng chưa được gọi là evidence-constrained calibration.

## Gate theo priority

1. Healthy baseline phải PASS frame, timestep, quaternion, manifest và finite
   checks.
2. Motor vigor và coordination chạy riêng từng proxy, nhiều seed.
3. Noise, delay và fatigue chỉ mở sau khi single-proxy artifacts ổn định.
4. Asymmetry cần mapping và metric review trước khi chạy.
5. Ba proxy chưa implement không được giả lập bằng cách đổi tên proxy khác.

