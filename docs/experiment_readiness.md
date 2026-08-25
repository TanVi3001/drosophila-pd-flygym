# Độ sẵn sàng của các experiment

## Phạm vi đánh giá

Đây là inventory của code và cấu hình hiện có, không phải xác nhận experiment
đã chạy. Audit hiện chưa có runtime FlyGym/MuJoCo hợp lệ và chưa có approved
numeric target data, vì vậy mọi experiment thực tế vẫn đang chờ gate.

## Bảng readiness

| Experiment/proxy | Đã implement? | Có thể chạy hiện tại? | Metric đang thu được | Metric chưa bảo đảm có |
| --- | --- | --- | --- | --- |
| Healthy baseline | Có, qua `healthy_baseline` và `run_demo.py` | Sau runtime PASS | frame, timestep, duration, planar displacement, path length, mean planar speed, heading yaw change, trajectory efficiency, finite/action/body-height checks | pause fraction, joint velocity/acceleration, COM-specific metric, symmetry và orientation stability nếu artifact không cung cấp |
| Motor Vigor | Có, `DiseaseLayer.motor_vigor`; campaign v1 bật | Chờ runtime và target gate | locomotion metrics của baseline và response theo parameter | metric riêng cho motor vigor |
| Coordination | Có, CPG coupling; campaign v1 bật | Chờ runtime và target gate | locomotion metrics của baseline và response theo parameter | metric riêng cho coordination hoặc gait |
| Noise | Có `motor_noise_std`; campaign hiện tắt | Chờ review cấu hình và gate | metric hiện có của rollout | metric riêng cho noise/stability |
| Delay | Có `initiation_delay_steps`; campaign hiện tắt | Chờ review cấu hình và gate | metric hiện có của rollout | metric initiation-specific |
| Fatigue | Có `fatigue_rate`; campaign hiện tắt | Chờ review cấu hình và gate | metric hiện có của rollout | metric fatigue-specific và kiểm định theo thời gian |
| Latency | Chưa có trường/state riêng | Không | Không có | latency metric và execution model |
| Freezing | Chưa có state freezing | Không | Không có | freezing event/probability và pause validation |
| Asymmetry | Có tham số nhưng cần left/right joint map; campaign tắt | Chưa an toàn | metric hiện có nếu mapping được xác nhận | symmetry index nếu chưa có mapping |
| Postural instability | Chưa có proxy postural/orientation riêng | Không | Không có metric riêng | postural sway/instability metric |

## Metric baseline hiện có

Các report baseline/campaign có thể ghi nhận các trường như `sample_count`,
`step_count`, `timestep_s`, `executed_duration_s`,
`planar_displacement_mm`, `planar_path_length_mm`,
`mean_planar_speed_mm_s`, `heading_yaw_change_rad`,
`trajectory_efficiency`, finite checks và body-height checks. Tên trường chính
thức phải đọc từ artifact thực tế sau mỗi lần chạy.

Pause fraction, joint RMS velocity/acceleration, COM velocity, symmetry index
và orientation stability chỉ được báo cáo khi analysis đã xuất chúng. Field
thiếu nghĩa là `unavailable`, không phải bằng 0.

## Gate hiện tại

- Runtime: `WAITING_RUNTIME` trong môi trường audit.
- Dataset thật: chưa có Healthy/PD rollout được xác nhận trong task này.
- Calibration target: file target hiện là template, chưa có giá trị số approved.
- Phenotype Atlas: chưa có record dữ liệu approved để làm target.
- Campaign v1: motor vigor và coordination bật; noise, delay, fatigue,
  asymmetry tắt; latency, freezing và postural instability chưa chạy được.

## Giới hạn diễn giải

Response curve chỉ mô tả quan hệ giữa tham số điều khiển và metric locomotion
trong simulation. Nó không chứng minh cơ chế bệnh học, không phải biological
validation, clinical prediction hoặc drug response.

## Future software improvement

Nếu nhóm cần latency, freezing hoặc postural instability, cần thiết kế và review
kỹ thuật riêng. Task này không implement thêm proxy hay mở rộng framework.

