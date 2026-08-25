# Release Readiness cho Calibration Study

## Boundary

Release này, nếu được thực hiện, sẽ phát hành artifact của một **computational locomotion model**.
Nó không phát hành biological Parkinson model, diagnostic
model, clinical prediction model, drug discovery model hay therapeutic
validation.

## Checklist

### Repository

- [ ] Commit/tag nghiên cứu đã khóa.
- [ ] `compileall`, pytest và `git diff --check` PASS.
- [ ] Không có source change ngoài scope được review.
- [ ] README, runtime matrix, changelog và version nhất quán.
- [ ] Không có secret, raw artifact nhạy cảm hoặc file lớn ngoài policy.

### Runtime

- [ ] Python 3.12.x.
- [ ] FlyGym 2.1.0.
- [ ] MuJoCo 3.9.0.
- [ ] `flygym_demo` import được.
- [ ] `scripts/check_runtime.py` PASS trên server đích.
- [ ] GPU/driver và storage được ghi lại nếu sử dụng.

### Dataset

- [ ] Healthy baseline đã chạy từ runtime thật.
- [ ] Mỗi dataset có rollout JSON/NPZ, viewer pose, manifest và metadata.
- [ ] Frame count, timestep, quaternion, finite values và checksum PASS.
- [ ] Raw dataset không bị ghi đè sau archive.
- [ ] Dataset/condition/seed inventory hoàn chỉnh.

### Figures và tables

- [ ] Figure blueprint được đối chiếu với output thực.
- [ ] Caption ghi dataset, seed, metric, đơn vị và boundary.
- [ ] Table có provenance, sample count, missingness và uncertainty khi có.
- [ ] Không có figure/table giả hoặc số liệu nhập tay không nguồn.

### Supplementary

- [ ] Config YAML và config hash.
- [ ] Seed list và runtime matrix.
- [ ] Manifest/checksum.
- [ ] Validation, loss và concordance report.
- [ ] Logs, failure/retry records và data management notes.

### Code Release

- [ ] Source commit được tag.
- [ ] Public API không thay đổi ngoài release scope.
- [ ] Test skips được giải thích.
- [ ] Installation và execution SOP đã được kiểm tra trên môi trường sạch.
- [ ] License, citation và contribution instructions nhất quán.

### Artifact Release

- [ ] Bundle có manifest và SHA-256.
- [ ] Artifact chỉ chứa kết quả của run đã validation.
- [ ] Viewer bundle trỏ đúng viewer pose.
- [ ] Có bản backup độc lập.
- [ ] Có release notes nêu rõ các artifact còn `WAITING_*`.

### Reproducibility

- [ ] Có thể dựng Python 3.12 runtime.
- [ ] Có thể tái chạy Healthy baseline.
- [ ] Seed, commit, versions, config và hardware được ghi.
- [ ] Nondeterminism và giới hạn tái lập được mô tả.
- [ ] Calibration/holdout split được lưu trước khi fit.

### Citation, DOI, License, GitHub Release, Zenodo

- [ ] Citation metadata được review.
- [ ] DOI chỉ điền sau khi repository/artifact thực sự được archive trên dịch
  vụ tương ứng.
- [ ] License được xác nhận, không tự suy đoán license còn thiếu.
- [ ] GitHub Release có tag, notes, manifest và checksum.
- [ ] Zenodo record được liên kết nếu nhóm chọn phát hành qua Zenodo.

## Blockers hiện tại

Release calibration chưa sẵn sàng vì runtime local đang `WAITING_RUNTIME`, chưa
có rollout thật được xác nhận, target calibration chưa được approve, evidence
chưa có quantitative paper count, và một số proxy chưa implement runtime.

## Điều kiện mở release

Chỉ chuyển sang READY sau khi runtime gate, Healthy validation, target review,
campaign artifacts, calibration/holdout, figures/tables và reproducibility
checklist đều có bằng chứng thật. Không dùng việc test phần mềm PASS để thay cho
scientific validation.
