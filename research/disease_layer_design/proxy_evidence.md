# Bằng chứng cho Disease Layer proxy

## Phạm vi

Bảng dưới đây được tổng hợp từ `results/evidence/coverage_report.csv`,
`parameter_importance.csv`, `dependency_matrix.csv` và `research_gap.md`.
Các con số là thống kê coverage của curation hiện tại. Chúng không phải effect
size, không phải prevalence và không phải bằng chứng chẩn đoán.

## Coverage theo proxy

| Proxy | Paper | Mapping | Quantitative | Qualitative | Calibration candidate | Validation candidate | Trạng thái |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `motor_vigor` | 15 | 19 | 0 | 15 | 15 | 15 | qualitative-only |
| `coordination` | 5 | 5 | 0 | 5 | 2 | 5 | qualitative-only |
| `delay` | 0 | 0 | 0 | 0 | 0 | 0 | no-literature |
| `noise` | 1 | 1 | 0 | 1 | 1 | 1 | qualitative-only |
| `fatigue` | 0 | 0 | 0 | 0 | 0 | 0 | no-literature |
| `latency` | 1 | 1 | 0 | 1 | 0 | 1 | qualitative-only |
| `asymmetry` | 0 | 0 | 0 | 0 | 0 | 0 | no-literature |
| `freezing` | 1 | 1 | 0 | 1 | 0 | 1 | qualitative-only |
| `postural_instability` | 6 | 6 | 0 | 6 | 3 | 5 | qualitative-only |

## Diễn giải theo độ mạnh mapping

`Strong`, `Moderate` và `Weak` trong metric-proxy matrix là nhãn được suy ra
từ confidence weight của Evidence Engine: HIGH, MEDIUM và LOW tương ứng.
Chúng biểu thị độ trực tiếp/độ tin cậy của mapping trong curation, không biểu
thị mức tác động sinh học.

| Metric | Proxy | Strength | Paper | Mapping | Mean evidence score | Ghi chú |
| --- | --- | --- | ---: | ---: | ---: | --- |
| climbing | motor_vigor | Strong | 8 | 10 | 68.5 | Metric tổng hợp; chưa tách vigor khỏi coordination/posture. |
| climbing | coordination | Weak | 1 | 1 | 53.0 | Chưa có decomposition. |
| flight | coordination | Moderate | 2 | 2 | 68.5 | Chưa tách cánh/thân. |
| speed; trajectory | motor_vigor | Strong | 1 | 1 | 82.0 | Numeric target chưa được approve. |
| geotaxis | motor_vigor | Strong | 1 | 1 | 77.0 | Cần giữ assay và tuổi riêng. |
| posture | postural_instability | Strong | 1 | 1 | 77.0 | Tư thế trực tiếp hơn morphology. |
| morphology | postural_instability | Strong | 2 | 2 | 77.0 | Static evidence, không thay orientation variance. |
| idling | freezing | Weak | 1 | 1 | 67.0 | Chưa có pause threshold. |
| time to finish | latency | Weak | 1 | 1 | 72.0 | Không tách latency khỏi các proxy khác. |

Các liên kết còn lại nằm đầy đủ trong `metric_proxy_matrix.csv`; ô trống trong
ma trận là thiếu evidence chứ không phải không có tác động.

## Parameter importance

Evidence Engine xếp hạng theo tổng Evidence Score:

1. `motor_vigor`: 15 paper, tổng 956.0, mean 63.733333.
2. `postural_instability`: 6 paper, tổng 353.0, mean 58.833333.
3. `coordination`: 5 paper, tổng 297.0, mean 59.4.
4. `noise`: 1 paper, mean 82.0.
5. `latency`: 1 paper, mean 72.0.
6. `freezing`: 1 paper, mean 67.0.
7. `delay`, `fatigue`, `asymmetry`: không có paper.

Đây là thứ tự ưu tiên curation và thiết kế thí nghiệm, không phải thứ tự
biological importance. Một proxy có điểm cao nhưng chỉ qualitative vẫn chưa
đủ điều kiện để fit tham số số học.

## Kết luận evidence hiện tại

- Có thể thiết kế các calibration candidate cho `motor_vigor`, một phần
  `coordination`, `noise` và `postural_instability` ở mức có điều kiện.
- Chưa có proxy nào có numeric target đã được xác minh trong bộ dữ liệu hiện
  tại.
- `delay`, `fatigue` và `asymmetry` cần curation bổ sung trước khi đưa vào
  calibration.
- Mọi paper có `manual_review_required=true` phải được review và approve trước
  khi trở thành target.

