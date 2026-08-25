# Benchmark Checklist

## Trước khi chạy

- [ ] Runtime matrix đã được kiểm tra.
- [ ] Python 3.12.x.
- [ ] FlyGym, MuJoCo và `flygym_demo` PASS.
- [ ] Git commit/tag và configuration đã khóa.
- [ ] Seed list đã khóa.
- [ ] Benchmark matrix đã được review.
- [ ] Healthy baseline protocol đã được review.
- [ ] Proxy implementation status đã được kiểm tra.

## Dataset và simulation

- [ ] Dataset directory đúng naming convention.
- [ ] Rollout JSON/NPZ đọc được.
- [ ] Frame count và steps đúng.
- [ ] Timestamps hợp lệ.
- [ ] Quaternion hợp lệ.
- [ ] Thorax displacement > 0 cho Healthy acceptance.
- [ ] Không NaN/Inf.
- [ ] Manifest và checksum PASS.
- [ ] Viewer pose khớp rollout.

## Metrics

- [ ] Metric definitions đã được khóa.
- [ ] Unit của từng metric được ghi.
- [ ] Formula variant được ghi nếu có nhiều implementation.
- [ ] Walking speed được chọn canonical variant.
- [ ] Path length và trajectory efficiency có denominator hợp lệ.
- [ ] COM metric chỉ dùng khi COM channel có thật.
- [ ] Pause threshold/minimum bout duration được ghi.
- [ ] Joint mapping và left/right mapping được xác nhận.
- [ ] Metric unavailable không bị thay bằng 0.

## Literature và calibration

- [ ] Literature record có provenance.
- [ ] Quantitative target được approve trước calibration.
- [ ] Assay, unit, sample size và uncertainty được ghi.
- [ ] Calibration/holdout split đã khóa.
- [ ] Không gọi technical sweep là biological range.
- [ ] Không suy diễn Parkinson từ response curve.

## Validation và statistics

- [ ] Đủ seed theo matrix.
- [ ] Pairing/independence structure đã xác định.
- [ ] Không dùng frames làm independent replicates.
- [ ] Missingness/outlier policy đã khóa.
- [ ] Bootstrap/permutation/mixed-effects condition được kiểm tra trước khi dùng.
- [ ] Effect size và confidence interval policy được ghi.
- [ ] Multiplicity policy được ghi.

## Paper package

- [ ] Figures.
- [ ] Tables.
- [ ] Supplementary artifacts.
- [ ] Captions có source, unit, seed và boundary.
- [ ] Reproducibility metadata.
- [ ] Code release.
- [ ] Artifact release.
- [ ] Citation.
- [ ] License.
- [ ] GitHub/Zenodo release plan.

## Scientific boundary

- [ ] Tất cả report gọi đúng đây là computational locomotion model.
- [ ] Không dùng “diagnosis”, “clinical prediction” hoặc “drug response” như kết quả.
- [ ] Không có biological conclusion khi chưa có dữ liệu phù hợp.

