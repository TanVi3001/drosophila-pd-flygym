# Các giả thuyết tính toán

Tài liệu này ghi các giả thuyết có thể kiểm định cho Disease Layer. Đây là
giả thuyết thiết kế, không phải kết luận sinh học và chưa được dùng để tạo
dataset hoặc chạy simulation trong Sprint 4.

## Nguyên tắc

- Mỗi giả thuyết phải gắn với một hoặc nhiều metric quan sát được.
- Không gán số liệu, ngưỡng hoặc hướng tác động nếu Evidence Engine chưa có
  outcome định lượng đã được duyệt.
- Phải tách assay, developmental stage, genotype, sex, age và protocol trước
  khi so sánh.
- Một metric có thể chịu ảnh hưởng của nhiều proxy; không được coi mapping là
  quan hệ nhân quả.

## Giả thuyết đơn proxy

### H1 - Motor vigor và output locomotion

Một thay đổi có kiểm soát ở proxy `motor_vigor` có thể làm thay đổi các output
locomotion như climbing, geotaxis, flight hoặc speed/trajectory. Kiểm định cần
giữ nguyên protocol và so sánh với healthy baseline cùng seed hoặc thiết kế
replicate tương đương.

**Điều kiện bác bỏ:** không có thay đổi nhất quán ở metric đích sau khi kiểm
soát nhiễu và protocol.

### H2 - Coordination và metric đa bộ phận

Một thay đổi ở `coordination` có thể ảnh hưởng các task cần phối hợp như flight,
crawling, angular change hoặc climbing. Evidence hiện tại chưa đủ để dự đoán
mức độ hay hướng thay đổi.

**Điều kiện bác bỏ:** proxy không tạo khác biệt ở metric coordination đã được
định nghĩa trước, hoặc khác biệt chỉ xuất hiện do motor vigor thay đổi.

### H3 - Noise và biến thiên trajectory

Một thay đổi ở `noise` có thể làm tăng biến thiên trajectory hoặc angular
change trong đúng treatment context được mô tả bởi paper. Không được dùng
mapping này như target baseline khi chưa xác minh context.

**Điều kiện bác bỏ:** biến thiên không khác healthy baseline trong cùng protocol,
hoặc khác biệt không lặp lại giữa các replicate.

### H4 - Latency và completion time

`latency` có thể liên quan `time to finish`, nhưng completion time cũng có thể
chịu ảnh hưởng bởi vigor, coordination và posture. Vì vậy đây là giả thuyết
phân biệt, không phải phép đồng nhất hai đại lượng.

**Điều kiện bác bỏ:** sau khi đo event-level latency, completion time không còn
liên hệ với latency.

### H5 - Freezing và idling

`freezing` chỉ nên được kiểm định sau khi có định nghĩa pause threshold và
episode duration. Mapping `idling` hiện tại chỉ là tín hiệu ứng viên.

**Điều kiện bác bỏ:** các episode idling không ổn định hoặc không phân biệt
được với thời gian nghỉ bình thường của healthy controller.

### H6 - Postural instability và posture/orientation

`postural_instability` có thể liên hệ với posture, morphology, flight hoặc
climbing, nhưng static morphology không thể thay thế time-resolved orientation.

**Điều kiện bác bỏ:** không có thay đổi ở orientation/COM/contact khi posture
được đo theo thời gian.

### H7 - Delay, fatigue và asymmetry là các proxy chưa sẵn sàng

Trong bộ evidence hiện tại, `delay`, `fatigue` và `asymmetry` không có mapped
paper. Giả thuyết phù hợp hiện nay là chưa thể đánh giá ba proxy này, không
phải chúng không tồn tại về mặt sinh học.

## Giả thuyết phối hợp

### H8 - Confounding giữa vigor và coordination

Climbing, flight và locomotion có thể thay đổi khi cả vigor và coordination
cùng thay đổi. Một calibration chỉ dùng các metric tổng hợp có thể không định
danh được từng proxy.

**Thiết kế kiểm định:** cần metric joint/stride/contact hoặc trajectory đã
harmonize để tách hai nguồn biến thiên.

### H9 - Tính cải thiện khi phối hợp nhiều proxy

Một mô hình kết hợp nhiều proxy chỉ đáng xem xét nếu cải thiện trên holdout
metrics mà không làm mất khả năng giải thích. Không được kết luận mô hình kết
hợp tốt hơn chỉ vì giảm loss trên calibration set.

**Thiết kế kiểm định:** so sánh single-proxy, multi-proxy và healthy baseline
trên cùng split dữ liệu với complexity penalty được ghi rõ.

## Dữ liệu cần bổ sung để kiểm định

1. Giá trị numeric, unit và uncertainty cho từng outcome.
2. Protocol và sample unit để không gộp assay không tương thích.
3. Event timestamps cho delay, latency và freezing.
4. Joint, stride, contact hoặc left-right data cho coordination/asymmetry.
5. Time-resolved posture, orientation và COM cho postural instability.
6. Replicate độc lập và holdout evidence được giữ ngoài quá trình fit.

