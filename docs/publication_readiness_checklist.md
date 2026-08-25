# Checklist sẵn sàng công bố

Đây là checklist kiểm soát chất lượng, không phải xác nhận repository đã sẵn
sàng xuất bản. Chỉ đánh dấu khi có bằng chứng/artifact thật và provenance.

## Runtime

- [ ] Python 3.12.x đã được khóa và ghi lại.
- [ ] FlyGym, MuJoCo và `flygym_demo` đúng runtime matrix.
- [ ] `scripts/check_runtime.py` trả PASS trên máy chạy thật.
- [ ] Môi trường có thể tái tạo từ project configuration.

## Simulation

- [ ] Healthy smoke run thành công.
- [ ] Config, seed, timestep và số bước được lưu.
- [ ] Không có thay đổi ngoài ý muốn trong simulation/FlyGym.
- [ ] Các run lỗi và lần retry được ghi rõ.

## Dataset

- [ ] Dataset thật có manifest và checksum.
- [ ] Raw rollout đọc được và frame count/timestamp hợp lệ.
- [ ] Viewer pose nhất quán với rollout.
- [ ] Metadata đủ provenance, genotype/condition và protocol khi có.
- [ ] Dataset acceptance validation trả PASS.

## Literature và calibration

- [ ] Paper đã được screening và provenance ghi nhận.
- [ ] Candidate phenotype đã manual review.
- [ ] Chỉ record được approve mới vào Phenotype Atlas.
- [ ] Calibration targets có đơn vị, uncertainty, assay và nguồn.
- [ ] Calibration/holdout split được khóa trước khi đánh giá.
- [ ] Không dùng qualitative-only evidence như numeric target.

## Validation và statistics

- [ ] Response curves có số seed và artifact nguồn.
- [ ] Cross-run consistency đã được kiểm tra.
- [ ] Validation report và limitation report đã được review.
- [ ] Phương pháp thống kê phù hợp với sample structure.
- [ ] Missingness, outlier và sensitivity được báo cáo.
- [ ] Không diễn giải vượt quá dữ liệu simulation.

## Figures và tables

- [ ] Figure manifest đã được đối chiếu với artifact thật.
- [ ] Mỗi figure có caption, nguồn dữ liệu và điều kiện chạy.
- [ ] Table có đơn vị, sample count, seed và phương pháp tổng hợp.
- [ ] Không có figure/table giả hoặc số liệu nhập tay không provenance.
- [ ] Viewer screenshot/export được lưu cùng pose và manifest tương ứng.

## Discussion và limitations

- [ ] Discussion chỉ nói về computational locomotion phenotype.
- [ ] Limitations nêu rõ thiếu biological validation nếu chưa có.
- [ ] Không gọi output là diagnosis, clinical prediction hoặc drug response.
- [ ] Future work tách biệt với kết quả đã chứng minh.

## Supplementary

- [ ] Config YAML, seed list và version matrix được cung cấp.
- [ ] Artifact manifest và checksum được cung cấp.
- [ ] Log và failure policy được mô tả.
- [ ] README/SOP cho người dùng độc lập đã được kiểm tra.

## Code release và artifact release

- [ ] Test suite PASS trên môi trường sạch hoặc có báo cáo skip rõ ràng.
- [ ] Compileall và `git diff --check` PASS.
- [ ] License, citation và changelog nhất quán.
- [ ] Không commit secret, raw data nhạy cảm hoặc file lớn ngoài policy.
- [ ] Release bundle có version, manifest và checksum.

## Reproducibility

- [ ] Người khác có thể dựng runtime theo hướng dẫn.
- [ ] Có thể chạy lại Healthy_001 mà không sửa notebook/code thủ công.
- [ ] Kết quả deterministic hoặc nguồn nondeterminism được ghi rõ.
- [ ] Backup và retention policy đã được áp dụng.

## Blocker hiện tại của repository

Checklist chưa thể đánh dấu PASS toàn bộ vì runtime Python 3.12/FlyGym/MuJoCo
chưa sẵn sàng, chưa có dataset thật được xác nhận, Phenotype Atlas còn thiếu
record approved và calibration target còn là template.

