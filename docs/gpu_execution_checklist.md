# Checklist chạy trên GPU server

Checklist này dành cho vận hành runtime thật. Không tự cài package, không tạo
rollout giả và không đánh dấu PASS nếu chưa có artifact tương ứng.

## A. Máy chủ và lưu trữ

- [ ] Máy chủ có quyền chạy job dài và volume persistent.
- [ ] Đã kiểm tra GPU bằng `nvidia-smi` nếu server dùng GPU.
- [ ] Có đủ dung lượng cho rollout, log, kết quả trung gian và backup.
- [ ] Có thư mục làm việc riêng, không chạy trực tiếp trên thư mục tạm.
- [ ] Đồng hồ hệ thống và timezone đã được ghi trong execution log.
- [ ] Có chính sách dừng job và tiếp tục job sau mất kết nối.

GPU không tự biến runtime thiếu FlyGym/MuJoCo thành runtime hợp lệ. Phải đạt
version gate trước.

## B. Python và dependency

- [ ] `python --version` trả về Python 3.12.x.
- [ ] Môi trường ảo đã được activate.
- [ ] Package đã được cài theo project configuration:

  ```bash
  python -m pip install -e ".[simulation,test]"
  ```

- [ ] FlyGym đúng phiên bản trong `docs/runtime_matrix.md`.
- [ ] MuJoCo đúng phiên bản trong `docs/runtime_matrix.md`.
- [ ] `flygym_demo` import được.
- [ ] Không có package cài thủ công ngoài manifest mà không ghi lại.

## C. Runtime gate và smoke test

- [ ] Chạy `python scripts/check_runtime.py`.
- [ ] Mọi mục bắt buộc của runtime report đều `PASS`.
- [ ] Chạy `python scripts/run_demo.py --steps 100`.
- [ ] Smoke simulation trả exit code 0.
- [ ] `datasets/healthy/Healthy_001/rollout.json` tồn tại.
- [ ] `rollout.npz` hoặc `rollout_arrays.npz` tồn tại.
- [ ] `viewer_pose.json`, `manifest.json`, `metadata.json` tồn tại.
- [ ] Frame count, timestamp và quaternion qua validation.

## D. Phân tích và viewer

- [ ] Chạy validation cho Healthy_001:

  ```bash
  python scripts/validate_research_workflow.py \
    --dataset datasets/healthy/Healthy_001 \
    --output results/validation/Healthy_001
  ```

- [ ] Chạy analysis:

  ```bash
  python scripts/analyze_rollout.py \
    --dataset datasets/healthy/Healthy_001 \
    --output results/analysis/Healthy_001
  ```

- [ ] Metrics output có frame count và duration hợp lệ.
- [ ] Chạy computational report/biomarker layer nếu campaign protocol yêu cầu.
- [ ] Viewer bundle mở được từ artifact vừa tạo; không dùng pose cũ.
- [ ] Camera, playback và trajectory được kiểm tra thủ công một lần.

## E. Campaign gates

- [ ] Approved numeric target data đã được nhóm review và lưu provenance.
- [ ] Campaign YAML đã được review, seed và parameter values đã khóa.
- [ ] Chạy campaign chỉ sau khi runtime và target gates đều PASS.
- [ ] Mỗi condition có manifest, seed, config hash và log riêng.
- [ ] Condition lỗi được giữ ở trạng thái FAILED, không bị ghi đè.
- [ ] Chưa bật latency, freezing hoặc postural instability khi proxy chưa có implementation.
- [ ] Báo cáo campaign có scientific boundary statement.

## F. Kết thúc job

- [ ] Validation cuối chạy không lỗi.
- [ ] Checksum và manifest đã được cập nhật.
- [ ] Log stdout/stderr đã được lưu.
- [ ] Backup đã được tạo trên volume khác.
- [ ] Đã ghi version, git commit, seed, hostname, GPU và thời gian chạy.
- [ ] Chỉ sau các bước trên mới upload artifact hoặc chuyển sang thống kê.

## Trạng thái audit hiện tại

Checklist này chưa được đánh dấu PASS cho một máy cụ thể. Audit repository hiện
đang chờ Python 3.12.x, FlyGym, MuJoCo và `flygym_demo` khả dụng.

