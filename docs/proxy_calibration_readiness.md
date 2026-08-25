# Proxy Calibration Readiness

## Phạm vi khoa học

Disease Layer hiện được xem là **computational locomotion model**: một lớp
perturbation ở mức controller/action để khảo sát response của locomotion
metrics. Đây không phải biological Parkinson model, diagnostic model, clinical
prediction model, drug discovery model hay therapeutic validation.

Báo cáo này là readiness audit, không phải kết quả calibration. Evidence
Engine hiện ghi nhận coverage qualitative-only cho các proxy có literature;
`quantitative_paper_count` hiện bằng 0 và `research/campaign/calibration_targets.csv`
còn là template rỗng. Vì vậy chưa có proxy nào đủ điều kiện để fit tham số vào
target số.

## Tóm tắt

| Proxy | Biological motivation | Literature support hiện có | Implementation hiện tại | Experimental readiness | Calibration readiness | Validation readiness | Hạn chế chính |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `motor_vigor` | Thay đổi output locomotion/vigor là endpoint có thể quan sát | 15 paper, qualitative-only | Có; `motor_vigor` | Có thể chạy sau runtime gate | Chưa: không có numeric target/unit được approve | Có thể kiểm tra response trên metrics hiện có | Không xác định cơ chế sinh học |
| `coordination` | Thay đổi phối hợp chân/gait có thể đo trong assay | 5 paper, qualitative-only | Có; CPG coupling | Có thể chạy sau runtime gate | Chưa: coordination metric chưa chuẩn hóa | Có thể kiểm tra contact/trajectory nếu artifact cung cấp | Coupling không phải synapse hay circuit measurement |
| `noise` | Biến thiên chuyển động có thể là endpoint | 1 paper, qualitative-only | Có trường `motor_noise_std`, campaign đang tắt | Cần review config rồi mới chạy | Chưa: chưa có target variance | Có thể kiểm tra seed/repeatability và variance | Noise không đồng nghĩa tremor |
| `delay` | Chậm khởi động có thể quan sát theo episode | Không có paper trong coverage | Có `initiation_delay_steps`, campaign đang tắt | Có thể chạy kỹ thuật sau review | Chưa: không có evidence/target | Cần episode boundary và timing protocol | Không phải neural reaction mechanism |
| `fatigue` | Suy giảm output theo thời gian có thể đo | Không có paper trong coverage | Có `fatigue_rate`, campaign đang tắt | Có thể chạy sau runtime và protocol | Chưa: không có longitudinal target | Cần rollout đủ dài và trend analysis | Không mô phỏng energy/muscle physiology |
| `latency` | Độ trễ sensorimotor có thể là endpoint assay | 1 paper, qualitative-only | Chưa có field/state trong Disease Layer | Không thể chạy bằng campaign hiện tại | Chưa | Chưa | Cần action buffer và timestamp contract |
| `freezing` | Movement arrest cần operational definition rõ | 1 paper, qualitative-only | Chưa có freezing state trong Disease Layer | Không thể chạy bằng campaign hiện tại | Chưa | Chưa | Pause assay không tự động là freezing |
| `asymmetry` | Chênh lệch trái/phải có thể quan sát | Không có paper trong coverage | Có tham số; cần left/right joint mapping, campaign tắt | Chưa an toàn cho runtime hiện tại | Chưa: không có target | Chỉ sau khi mapping và symmetry metric được xác nhận | Không suy ra laterality sinh học |
| `postural_instability` | Orientation/COM instability có thể là endpoint | 6 paper, qualitative-only | Chưa có proxy postural riêng | Không thể chạy bằng campaign hiện tại | Chưa | Chưa | Chưa có stabilizer và metric contract |

## Đánh giá chi tiết

### `motor_vigor`

- **Biological motivation:** dùng thay đổi vigor như một locomotion endpoint,
  không gán nguyên nhân tế bào.
- **Computational interpretation:** gain trên action components đã khai báo.
- **Metrics cần theo dõi:** mean planar speed, path length, displacement,
  trajectory efficiency và joint velocity nếu rollout xuất.
- **Healthy default:** giá trị healthy hiện có trong controller/config.
- **Calibration candidate:** các điểm trong config chỉ là technical sweep;
  chưa phải range sinh học.
- **Validation:** multi-seed repeatability, monotonicity nếu được đặt trước,
  holdout metric.

### `coordination`

- **Biological motivation:** khảo sát locomotion coordination ở mức quan sát.
- **Computational interpretation:** retained CPG coupling scale.
- **Metrics cần theo dõi:** contact timing, trajectory efficiency, turning,
  heading variance và joint metrics nếu có.
- **Healthy default:** coupling mặc định của healthy controller.
- **Calibration candidate:** giá trị config hiện có chỉ để khảo sát response.
- **Validation:** contact/coordination protocol, seed consistency và metric
  availability.

### `noise`

- **Biological motivation:** khảo sát movement variability.
- **Computational interpretation:** `motor_noise_std` có seed và phân phối
  phải ghi rõ.
- **Metrics cần theo dõi:** variance của speed/heading/joint output nếu có.
- **Readiness:** code field có, nhưng campaign tắt và chưa có target variance.

### `delay` và `fatigue`

Hai proxy có trường controller tương ứng, nhưng evidence hiện không cung cấp
numeric target. Chỉ nên chạy sensitivity/response characterization sau khi
protocol, observation window và metric definition được nhóm review.

### `latency`, `freezing`, `postural_instability`

Các proxy này nằm trong design/evidence vocabulary nhưng chưa có implementation
runtime hoàn chỉnh. Không được coi configuration placeholder là experiment.

### `asymmetry`

Tham số tồn tại nhưng validation phụ thuộc mapping left/right. Chưa chạy trước
khi mapping, sign convention và symmetry metric được xác nhận bằng artifact thật.

## Điều kiện mở calibration

1. Runtime matrix PASS trên Python 3.12, FlyGym, MuJoCo và `flygym_demo`.
2. Healthy rollout PASS validation.
3. Evidence record có provenance, assay, unit và reviewer.
4. Calibration target số được approve; target hiện chưa có.
5. Calibration/holdout split và loss protocol được khóa trước khi chạy.
6. Metrics cần fit tồn tại trong output; metric thiếu phải ghi `unavailable`.

