# Paper Figure Blueprint

## Scientific scope

Các figure dưới đây chỉ được tạo sau khi có artifact simulation thật. Nội dung
trình bày **computational locomotion model**, không phải biological Parkinson
model, diagnostic model, clinical prediction model, drug discovery model hay
therapeutic validation. Không tạo figure placeholder để thay cho dữ liệu.

## Blueprint

| Figure | Nội dung | Nguồn dữ liệu | Module/artefact tạo | Caption bắt buộc | Điều kiện phát hành |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | System Overview | Architecture và workflow docs | Documentation/manual diagram | Nêu rõ Healthy Controller -> Disease Layer -> FlyGym -> metrics -> calibration | Không chứa kết quả nếu chỉ là sơ đồ |
| Figure 2 | Disease Layer | Parameter/config manifest đã review | Disease Layer design/config | Proxy, parameter convention, healthy identity và boundary | Không gán parameter với neuron/gene |
| Figure 3 | Experimental Campaign | Campaign manifest, seeds, condition inventory | Experimental Campaign output | Số condition, seed, steps, status | Chỉ dùng run PASS và ghi run lỗi |
| Figure 4 | Response Surface | `response_surface.csv/json` từ simulation thật | Campaign response surface | Parameter value, metric, seed count và missingness | Không gọi surface là disease severity |
| Figure 5 | Calibration Result | Approved targets, fitted parameters, holdout report | Calibration Framework output | Target provenance, loss, uncertainty và holdout | Chỉ tạo khi target số đã approved |
| Figure 6 | Concordance Matrix | Evidence, campaign metrics, concordance output | Concordance Framework | Agreement status và evidence level | Không tính biological similarity hoặc clinical validity |
| Figure 7 | Limitations | Validation report và research gaps | Report/manual curation | Những metric, proxy, dataset và assay còn thiếu | Phải phản ánh artifact thật |
| Figure 8 | Future Work | Research plan, không phải result | Documentation | Các bước tương lai được tách khỏi findings | Không minh họa kết quả chưa có |

## Quy tắc caption

Mỗi caption phải ghi:

1. dataset/condition và số seed;
2. thời lượng, timestep hoặc steps;
3. metric, đơn vị và cách tổng hợp;
4. version/config/commit khi cần tái lập;
5. trạng thái missing hoặc unavailable;
6. câu boundary: đây là computational locomotion output, không phải biological
   hoặc clinical validation.

## Trạng thái hiện tại

Chưa có figure khoa học nào được sinh trong Sprint này. Figure 1, 2, 7 và 8 có
thể được hoàn thiện dưới dạng thiết kế tài liệu; Figure 3--6 cần runtime,
dataset thật, approved targets và output hợp lệ.

