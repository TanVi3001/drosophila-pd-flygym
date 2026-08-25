# Statistical Analysis Plan

## Phạm vi

Đây là kế hoạch lựa chọn phương pháp, không phải phân tích đã chạy. Chỉ dùng
artifact simulation thật và không tạo statistical result giả. Mọi phân tích
chỉ mô tả response của **computational locomotion model**; không phải biological
Parkinson validation, diagnosis, clinical prediction, drug discovery hay
therapeutic validation.

## Nguyên tắc trước khi chọn test

Nhóm nghiên cứu phải xác định trước:

- đơn vị quan sát: seed, rollout, animal/source dataset hay frame;
- paired hay independent design;
- proxy/condition và Healthy baseline;
- metric definition, unit, observation window;
- missingness và rule loại run;
- primary/secondary endpoints;
- multiplicity policy;
- random seed và software/runtime versions.

Không coi frames trong cùng một rollout là independent replicates. Không chọn
test chỉ vì nó cho p-value thuận lợi.

## Bootstrap

**Mục đích:** ước lượng uncertainty của mean, median, delta baseline-condition,
hoặc effect summary khi có đủ independent rollout/seed.

**Chỉ áp dụng khi:** số rollout đủ để resample có ý nghĩa, unit of resampling
được xác định, metric finite và design paired được bootstrap theo cặp nếu cần.

**Cần khóa trước:** số resamples, statistic, percentile/BCa interval, random
seed và missing-data rule. Bootstrap không sửa vấn đề pseudoreplication giữa
frames.

## Permutation test

**Mục đích:** kiểm tra difference giữa hai condition khi exchangeability phù
hợp, đặc biệt với paired seed hoặc baseline-condition pairing.

**Chỉ áp dụng khi:** null hypothesis và permutation unit được định nghĩa,
pairing được giữ nguyên, số hoán vị hoặc enumeration được khóa, và condition
labels có thể exchange được theo design.

**Cần báo cáo:** statistic, số permutations, exact/randomized method, seed,
one/two-sided policy và multiplicity correction nếu có nhiều metrics.

## Mixed-effects model

**Mục đích:** mô hình hóa nhiều seed/condition/batch hoặc repeated measures khi
có cấu trúc phân cấp thật.

**Chỉ áp dụng khi:** có đủ cấp của random effect, ví dụ batch/experiment/source
dataset, có replication trong mỗi cấp và sample structure hỗ trợ model. Không
dùng mixed effects chỉ vì có nhiều frames.

**Cần khóa trước:** fixed effects, random intercept/slope, link/transform,
covariates, estimation method, convergence checks và sensitivity model.

## Effect size

Effect size phải được chọn theo design và metric, có uncertainty nếu có thể:

- paired mean/median difference hoặc standardized paired effect;
- rank-based effect khi phân phối/scale không phù hợp;
- variance or ratio effect khi câu hỏi nhắm vào variability.

Không gọi effect size là disease severity. Cần nêu direction convention và
biological/computational interpretation giới hạn trong protocol.

## Confidence interval

CI có thể được xây dựng bằng bootstrap, model-based interval hoặc phương pháp
phù hợp với test đã chọn. Phải ghi confidence level, estimator, unit of
resampling và multiplicity. CI không chứng minh biological validity nếu target
literature không tương thích.

## So sánh nhiều metric/condition

Nếu có nhiều endpoints hoặc nhiều parameter values, nhóm phải định nghĩa primary
endpoint trước, sau đó chọn multiplicity control phù hợp. Không báo cáo hàng
loạt p-value không hiệu chỉnh như thể là các hypothesis độc lập.

## Quality gates trước phân tích

1. Runtime và dataset acceptance PASS.
2. Tất cả run có cùng timestep/duration hoặc khác biệt đã được protocol hóa.
3. Metric unit và formula khớp giữa baseline/condition.
4. Không có NaN/Inf trong sample được phân tích.
5. Số seed và pairing đủ theo analysis design.
6. Missingness, outlier và sensitivity report đã được lưu.

Nếu một điều kiện chưa đạt, trạng thái là `WAITING_DATA` hoặc `NOT_APPLICABLE`,
không chạy test và không tạo số liệu thay thế.

## Scientific boundary

Kết quả thống kê, nếu được chạy sau này, chỉ quantifies computational response
trong simulation. Nó không chứng minh cơ chế Parkinson, giá trị lâm sàng, khả
năng chẩn đoán, đáp ứng thuốc hay hiệu quả điều trị.

