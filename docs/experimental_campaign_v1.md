# Experimental Campaign v1

## Mục đích

Campaign này là workflow orchestration để đo response của locomotion metrics
khi thay đổi từng control-level proxy đã có trong `DiseaseLayer`. Đây là
computational locomotion experiment, không phải biological validation, clinical
prediction hoặc drug response.

Campaign không tạo rollout, metric hay response surface khi runtime hoặc target
gate chưa đạt. Mọi kết quả định lượng phải đến từ simulation FlyGym thật và
được ghi kèm seed, condition và report nguồn.

## Cách chạy

```powershell
python scripts/run_experimental_campaign.py
```

Cấu hình mặc định nằm tại
`configs/experiments/campaign_v1.yaml`. Có thể thay campaign, baseline, target
và thư mục output bằng các cờ CLI tương ứng:

```powershell
python scripts/run_experimental_campaign.py `
  --campaign configs/experiments/campaign_v1.yaml `
  --baseline-config configs/experiments/healthy_baseline.yaml `
  --targets configs/parkinson/phenotype_database.json `
  --output results/experimental_campaign
```

## Execution gates

1. **Runtime gate**: Python, FlyGym, MuJoCo và `flygym_demo` phải sẵn sàng.
2. **Target gate**: phải có numeric calibration targets đã được phê duyệt.
3. Chỉ khi cả hai gate `PASS`, runner mới gọi `run_locomotion` hiện có.

Nếu gate đầu tiên không đạt, trạng thái là `WAITING_RUNTIME`. Nếu runtime đạt
nhưng target chưa đạt, trạng thái là `WAITING_TARGET_DATA`. Hai trạng thái này
không tạo dataset giả, response surface, sensitivity ranking hay figure.

## Proxy được hỗ trợ

Trong `DiseaseLayer` hiện có thể sweep:

- `motor_vigor` -> `motor_vigor`
- `coordination` -> `coordination`
- `noise` -> `motor_noise_std`
- `delay` -> `initiation_delay_steps`
- `fatigue` -> `fatigue_rate`
- `asymmetry` -> `asymmetry`, chỉ sau khi có mapping khớp trái/phải đã xác minh

`latency`, `freezing` và `postural_instability` được liệt kê trong campaign để
theo dõi phạm vi, nhưng đang tắt vì `DiseaseLayer` hiện có chưa cung cấp trường
tương ứng. Runner không giả lập các proxy này.

## Metric collection

Runner chỉ đọc các key đã có trong `derived_locomotion_metrics` của pipeline:

- walking speed
- path length
- trajectory efficiency
- và các metric khác nếu report thật cung cấp

COM displacement, heading variance, pause fraction, joint velocity,
orientation stability và symmetry index được ghi là `UNAVAILABLE_METRIC` khi
nguồn hiện tại không xuất chúng. Không thay thế bằng metric gần nghĩa và không
suy diễn giá trị bị thiếu.

## Artifact

Khi chạy thành công, `results/experimental_campaign/` có:

```text
baseline/
conditions/
campaign_data.json
campaign_status.json
campaign_status.md
experiment_summary.md
response_surface.csv
response_surface.json
response_surface.md
parameter_sensitivity.csv
parameter_sensitivity.json
parameter_sensitivity.md
```

`parameter_sensitivity` chỉ là xếp hạng độ nhạy computational dựa trên
normalized delta so với Healthy baseline. Nó không phải severity score và không
được dùng để kết luận bệnh học.

## Trạng thái hiện tại

Trong môi trường thiếu runtime, hãy kiểm tra
`results/experimental_campaign/campaign_status.json`. Không đọc các file output
cũ như bằng chứng của lần chạy hiện tại nếu status là `WAITING_RUNTIME` hoặc
`WAITING_TARGET_DATA`.
