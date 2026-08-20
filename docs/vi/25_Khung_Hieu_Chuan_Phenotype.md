# Khung hiệu chuẩn phenotype tính toán

## Phạm vi

Khung này thêm một lớp biến đổi ở mức điều khiển quanh CPG khỏe mạnh hiện có.
Nó không phải mô hình não sinh học, không dùng trọng số neuron, không đặt
ngưỡng lâm sàng và không mô phỏng điều trị. Các tham số phải được báo cáo là
proxy tính toán.

## Luồng dữ liệu

```text
CPG khỏe mạnh
  -> DiseaseLayer
  -> mô phỏng FlyGym hiện có
  -> rollout metrics
  -> quan sát từ y văn có provenance
  -> grid calibration xác định
  -> đánh giá holdout độc lập
```

`DiseaseLayer` có các trường motor vigor, coordination, initiation delay,
motor noise, fatigue và asymmetry. Mỗi phép biến đổi có công thức công khai,
seed và metadata. Bản đồ trái/phải phải do người dùng cung cấp; package không
tự đoán mapping giải phẫu.

## Dữ liệu y văn

Mỗi target cần source, citation, model context, assay, metric và unit. Quan sát
định tính được giữ để truy xuất nguồn nhưng không được tự đổi thành con số.
Template `configs/parkinson/phenotype_database.template.json` không chứa số
liệu sinh học giả.

## Calibration

`calibrate_grid()` nhận evaluator do caller cung cấp, nên vẫn tái sử dụng runner
FlyGym hiện tại. Engine chỉ tính sai số chuẩn hóa có trọng số, ghi rõ metric
thiếu, chọn candidate hoàn chỉnh có loss nhỏ nhất và chấm holdout nếu có.

Khi chưa có target số phù hợp đơn vị và đúng assay, trạng thái là
`UNAVAILABLE_NUMERIC_TARGET`. Một fit thành công chỉ là sự phù hợp tính toán
với các quan sát đã nhập, không phải xác nhận cơ chế bệnh hay giá trị lâm sàng.

## Chạy các computational conditions

Sau khi Healthy baseline PASS, chạy:

```bash
python scripts/run_calibration_conditions.py \
  --conditions configs/parkinson/calibration_conditions.yaml \
  --output results/calibration_conditions
```

Lệnh gọi lại `run_locomotion()` hiện có, không tạo simulation engine mới.
Kết quả gồm report của baseline, report của từng condition và `summary.json`.
Chỉ thêm `--targets` khi đã có target số được trích xuất đúng đơn vị, assay và
nguồn. Template hiện tại chỉ là quan sát định tính nên trạng thái calibration
sẽ là `UNAVAILABLE_NUMERIC_TARGET`, đây là kết quả đúng và không phải lỗi.
