# Metric Definition

## Phạm vi

Các định nghĩa dưới đây dùng cho benchmark rollout. Repository có nhiều lớp
phân tích, vì vậy tên field cụ thể phải được ghi kèm trong artifact. Đây là
metric của **computational locomotion model**, không phải biological Parkinson
measurement, clinical endpoint hay diagnostic output.

| Metric | Ý nghĩa | Công thức/định nghĩa trong repository | Đơn vị | Calibration | Validation | Publication |
| --- | --- | --- | --- | --- | --- | --- |
| Walking speed | Tốc độ di chuyển của thorax trên mặt phẳng | Có hai variant: `mean_planar_speed_mm_s = planar_displacement / executed_duration`; rollout analysis dùng mean instantaneous speed, trong đó sample đầu bằng 0 | mm/s | Có | Có | Có |
| Path length | Tổng quãng đường thorax đi qua | `sum(norm(diff(thorax_xy)))` | mm | Có | Có | Có |
| Trajectory efficiency | Mức thẳng của quỹ đạo so với đường đi thực tế | `planar_displacement / planar_path_length` khi path length > 0; nếu không thì unavailable | không thứ nguyên, thường 0--1 | Có | Có | Có |
| COM displacement | Độ dời của COM | Repository lưu COM trajectory và COM velocity; chưa định nghĩa một scalar canonical tên COM displacement | mm nếu được đăng ký | Conditional | Có nếu channel đủ | Conditional |
| Heading variance | Độ biến thiên hướng yaw | `var(unwrap(heading_rad))` trong rollout analysis | rad² | Conditional | Có | Có |
| Pause fraction | Phần thời gian không vượt ngưỡng tốc độ | Behavior platform dùng `immobility_ratio = pause_duration / total_duration`; threshold và minimum bout duration phải ghi trong config | không thứ nguyên | Conditional | Có | Có |
| Joint velocity | Tốc độ thay đổi của joint position/action | Nếu thiếu channel velocity, analysis có thể dùng gradient theo time; `joint_rms_velocity = sqrt(mean(joint_velocity²))` theo joint | theo channel nguồn, thường rad/s | Conditional | Có | Có |
| Symmetry index | Mức tương đồng trái/phải | Với cặp L/R: `1 - abs(L - R) / (L + R)` khi tổng > 0; index cuối là mean các cặp | không thứ nguyên | Conditional | Có nếu mapping đủ | Conditional |
| Orientation stability | Độ ổn định orientation của body | Repository có `body_orientation_variance`: mean của variance roll, pitch, yaw; lower variance không tự động là “healthy” | rad² | Conditional | Có | Có |

## 1. Walking speed

`metrics/locomotion.py` dùng planar displacement chia cho executed duration.
`analysis/rollout_analysis.py` có field `walking_speed_mm_s` được tính từ mean
instantaneous speed, trong đó sample đầu là 0; `trajectory.py` có
`mean_step_speed_mm_s` không gắn cùng tên. Benchmark phải chọn một variant,
ghi field name và không trộn các variant trong cùng comparison.

## 2. Path length và trajectory efficiency

Path length là tổng khoảng cách Euclidean giữa các thorax XY samples liên tiếp.
Planar displacement là khoảng cách Euclidean giữa điểm đầu/cuối. Efficiency chỉ
có nghĩa khi path length dương và phải được báo `unavailable` nếu denominator
không hợp lệ.

## 3. COM displacement

Rollout analysis hiện hỗ trợ `com_trajectory`, `com_velocity_mm_s` và
`com_velocity_mean_mm_s`. Repository chưa định nghĩa scalar `COM displacement`
chính thức. Trước khi dùng trong calibration hoặc paper, nhóm phải đăng ký rõ
đó là endpoint đầu-cuối hay path length của COM, cùng unit và window. Không tự
đổi thorax displacement thành COM displacement.

## 4. Heading variance và orientation stability

Quaternion được chuyển sang heading/yaw theo convention `wxyz`, unwrap trước
khi tính variance. Orientation variance hiện là trung bình variance của roll,
pitch và yaw. Đây là biến thiên hình học trong simulation, không phải đo postural
control sinh học.

## 5. Pause fraction

Pause phụ thuộc speed threshold và minimum bout duration. Hai điều kiện phải
được cố định giữa baseline và condition. `pause_fraction` là tên protocol;
artifact hiện có thể dùng `immobility_ratio` hoặc pause duration fields.

## 6. Joint velocity và symmetry

Joint velocity phải có source channel hoặc được tính bằng differentiation theo
timestamp. Symmetry chỉ hợp lệ khi cặp trái/phải được nhận diện rõ; nếu thiếu
mapping, ghi `unavailable` thay vì suy luận từ tên joint mơ hồ.

## 7. Missingness rule

Metric thiếu channel, thiếu unit hoặc denominator không hợp lệ phải được ghi
`unavailable`/`conditional`. Không thay bằng 0, không nội suy từ metric khác và
không đưa vào loss/statistics như observation hợp lệ.

