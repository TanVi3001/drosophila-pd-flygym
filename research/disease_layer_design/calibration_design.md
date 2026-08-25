# Thiết kế calibration

## 1. Mục tiêu

Calibration sẽ tìm parameter set của computational Disease Layer phù hợp với
calibration targets đã được trích xuất và approve từ literature. Sprint 4 chỉ
định nghĩa quy trình; chưa fit parameter, chưa chạy simulation và chưa tạo
numeric target.

## 2. Giai đoạn chuẩn bị bắt buộc

1. Hoàn tất curation cho paper có mapping candidate.
2. Xác minh DOI/PMID, genotype, assay, age, sex, temperature, sample unit và
   protocol.
3. Trích value, unit, variance/uncertainty, figure/table/page và provenance.
4. Approve từng candidate trong manual review.
5. Harmonize metric theo assay và developmental stage; không gộp climbing,
   flight, crawling, geotaxis và continuous walking nếu chưa có quy tắc.
6. Chia calibration evidence và holdout evidence trước khi chạy optimizer.

## 3. Target và loss

Mỗi target cần có dạng khái niệm:

```text
literature target
    -> normalized metric
    -> simulation metric
    -> uncertainty-aware discrepancy
    -> weighted loss
```

Loss chỉ được tính trên metric tương thích. Trọng số phải đến từ protocol đã
phê duyệt hoặc uncertainty; không dùng Evidence Score như effect size. Nếu
target thiếu unit, variance hoặc assay metadata thì ghi `not_ready`, không tự
điền.

## 4. Thứ tự ưu tiên hiện tại

1. `motor_vigor` với climbing, geotaxis và speed/trajectory sau khi numeric
   values được approve.
2. `coordination` với flight hoặc metric joint/stride trực tiếp.
3. `postural_instability` với posture/orientation/COM time series.
4. `noise` chỉ trong treatment context có provenance tương ứng.
5. `latency` sau khi có event-level latency, không chỉ time to finish.
6. `freezing` sau khi có pause threshold và episode duration.
7. `delay`, `fatigue`, `asymmetry` chỉ sau khi lấp research gap.

Đây là thứ tự thu thập và thiết kế thí nghiệm, không phải xếp hạng hiệu lực
sinh học.

## 5. Identifiability

Một parameter không được fit riêng nếu metric đích chịu ảnh hưởng tương tự từ
nhiều proxy. Cụ thể:

- climbing có thể confound motor vigor, coordination và posture;
- flight có thể confound coordination và posture;
- time to finish có thể confound latency, vigor và coordination;
- idling chưa đủ để xác định freezing.

Thiết kế cần single-proxy ablation, multi-proxy comparison và holdout để kiểm
tra parameter có được nhận diện hay chỉ overfit metric tổng hợp.

## 6. Acceptance criteria đề xuất

Calibration chỉ được đánh dấu `ready_for_review` khi:

- mọi target được provenance và unit hóa;
- tất cả output simulation finite và có manifest;
- healthy baseline chạy cùng protocol;
- calibration và holdout được báo cáo riêng;
- kết quả có uncertainty/replicate summary nếu nguồn cho phép;
- không có kết luận vượt quá computational scope.

Không đặt ngưỡng số học trong Sprint 4 vì chưa có target quantitative được
approve.

## 7. Outputs dự kiến của giai đoạn sau

- parameter manifest và source provenance;
- calibration configuration;
- baseline và fitted simulation artifacts;
- metric-level loss table;
- holdout report;
- sensitivity/ablation report;
- failure log nếu target không tương thích.

