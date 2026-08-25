# Paper Table Blueprint

## Scientific scope

Tables chỉ được điền từ evidence có provenance hoặc artifact simulation thật.
Chúng mô tả một **computational locomotion model**, không phải biological
Parkinson model, diagnostic model, clinical prediction model, drug discovery
model hay therapeutic validation.

## Blueprint

| Table | Nội dung | Columns/fields dự kiến | Nguồn | Điều kiện sử dụng |
| --- | --- | --- | --- | --- |
| Table 1 | Literature Summary | paper ID, gene/condition, assay, sample size, metric, unit, provenance, evidence level | Approved literature records/Phenotype Atlas | Không điền paper chưa review; qualitative-only phải gắn nhãn |
| Table 2 | Disease Layer Proxy | proxy, implementation status, parameter, healthy default, literature coverage, target status, limitation | Evidence Engine, Disease Layer Design | Không ghi numeric range nếu `NOT_PROPOSED` |
| Table 3 | Calibration Results | proxy, parameter value, seed count, metric, loss, uncertainty, holdout status | Calibration output thật | Chỉ sau approved numeric targets và completed runs |
| Table 4 | Validation Results | validation item, expected contract, observed value, status, artifact, warning | Validation/concordance reports | Không chuyển `unavailable` thành PASS |
| Table 5 | Limitations | limitation, evidence, affected proxy/metric, consequence, mitigation/future work | Research gaps, audit và reports | Phân biệt software limitation với scientific limitation |

## Table notes bắt buộc

- Ghi rõ đơn vị, sample count và seed count.
- Ghi missingness thay vì loại âm thầm các dòng thiếu.
- Giữ liên kết tới DOI/PMID hoặc artifact manifest khi có.
- Không suy diễn mức độ Parkinson từ một metric hay proxy.
- Nêu rõ các giá trị chỉ là technical sweep và không phải biological range.

## Trạng thái hiện tại

Chưa có bảng kết quả được sinh trong Sprint này. Table 1 và Table 2 có thể
chuẩn bị từ record đã review/config; Table 3 và Table 4 chờ runtime, dataset và
validation; Table 5 chờ audit kết quả thật.

