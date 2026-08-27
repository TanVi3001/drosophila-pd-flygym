# Đối chiếu tài liệu nhóm với repository

## Phạm vi

Tài liệu được đối chiếu là `De_Cuong_NCKH_Drosophila_Parkinson_Hoan_Chinh.docx`
và archive `drosophila_pd_all_videos.zip` do người dùng cung cấp. Đây là review
đầu vào nghiên cứu, không phải xác minh độc lập toàn bộ trích dẫn hay kết quả
sinh học.

## Kết luận ngắn

Nhóm đã có một nền tảng mô phỏng FlyGym/MuJoCo, recorder, export, viewer mesh,
metrics, Disease Layer ở mức action/controller và các workflow calibration,
concordance, provenance. Repo hiện có thể chạy một condition computational và
so sánh nó với healthy baseline.

Tài liệu DOCX mô tả một phạm vi rộng hơn nhiều: cầu nối gen → LIF → CPG → cơ
học 3D, bảy mô hình gene, tiến triển 30 ngày, N=6, climbing assay và đối chuẩn
định lượng. Trong source tree hiện tại, các claim về LIF/brain-driven bridge,
`data/bridge_scales`, các script `run_brain_driven_*` và `run_30day_progression.py`
không được tìm thấy. Do đó chúng phải được trình bày là kế hoạch hoặc phần việc
của codebase khác cho tới khi nhóm cung cấp source commit tương ứng.

## Ma trận đối chiếu

| Nội dung trong DOCX | Bằng chứng trong repo hiện tại | Trạng thái đúng nhất |
| --- | --- | --- |
| FlyGym/MuJoCo embodied simulation | `src/drosophila_pd/flygym_adapter/`, runtime check, integration tests | Có trong repo |
| Healthy locomotion baseline | `src/drosophila_pd/experiments/healthy_baseline.py`, config healthy | Có, cần ghi rõ runtime/seed |
| CPG controller | Controller FlyGym chính thức được dùng trong baseline | Có ở tầng điều khiển; không đồng nghĩa LIF |
| Disease Layer | `src/drosophila_pd/parkinson/disease_layer.py` và perturbations | Có ở mức proxy action/controller |
| LIF / gene-to-neuron bridge | Không thấy package/module/source tương ứng trong tree hiện tại | Chưa chứng minh trong repo |
| Bảy gene model với `bridge_scales` | Không có `data/bridge_scales` trong repo hiện tại | Chưa chứng minh trong repo |
| 30 ngày, 21 mốc | Không có script `run_30day_progression.py` | Chưa chứng minh trong repo |
| N=6 Wilcoxon | Có thiết kế/workflow liên quan, nhưng cần chạy lại từ artifact thật trước khi dùng số liệu | Chưa phải kết quả mới được xác nhận |
| Climbing assay | Phạm vi hiện tại chủ yếu là flat-ground locomotion | Khoảng trống đã biết |
| Viewer mesh thật | Mesh FlyGym được materialize qua `viewer_export` và bundle | Có; đây là visualization của rollout |
| Archive video/JSON nhóm gửi | 8 MP4 + 7 JSON report, không có rollout thô/viewer pose | Artifact dẫn xuất, cần provenance |

## Điều archive chứng minh được

- Có 7 JSON report parse được, đều ghi `overall_pass=true`.
- Các report có cặp baseline/perturbed và metric locomotion dẫn xuất.
- Có 8 file MP4 và hash được ghi trong audit.
- Các report ghi nguồn ngoài repository (`bridge_scales`/`fly-brain`).
- Archive không đủ để tái lập toàn bộ rollout hoặc mở viewer độc lập.

## Không khớp với số liệu trong DOCX

Bảng `Δ%sim` trong DOCX không thể được xem là kết quả đã xác minh từ archive.
Khi đối chiếu các trường speed/yaw trong 7 JSON, có sai khác đáng kể:

| Model | Archive: thay đổi speed | Archive: thay đổi yaw | DOCX ghi |
| --- | ---: | ---: | --- |
| `pink1` | +14.657% | +21.375% | +12.8% |
| `parkin` | -4.628% | +44.055% | +47.2% yaw |
| `lrrk2` | +13.646% | +44.436% | +42.9% yaw |
| `complexI` | +11.229% | +13.758% | -14.2% |
| `pink1_age25` | -15.003% | +47.662% | -28.9% |
| `pink1_parkin_OE_age25` | -4.671% | +11.748% | -5.1% |

Bảng này chỉ là phép đối chiếu file, không phải đánh giá sinh học. Do DOCX
không luôn chỉ rõ metric của `Δ%sim`, protocol có thể khác; tuy vậy chênh lệch
này đủ để nhóm phải tái sinh số liệu từ source commit/config/seed được đóng
băng trước khi dùng trong đề cương. Archive hiện cũng ghi `git_commit: null` và
tham chiếu `data/bridge_scales` ngoài repo.

Các con số này là kiểm tra cấu trúc và provenance của file, không phải kết luận
rằng condition là Parkinson, không phải validation sinh học và không phải dữ
liệu thực nghiệm của ruồi sống.

## Việc nên làm tiếp theo

1. Đóng băng commit và runtime của code đã tạo archive.
2. Chạy lại từng condition từ source commit đó, xuất rollout thô, manifest,
   checksum và config/seed cùng một gói.
3. Kiểm tra từng paper, assay, đơn vị, figure/table và phê duyệt mapping trước
   khi đưa vào calibration target.
4. Chạy multi-seed và holdout theo protocol đã định trước; không dùng chính các
   giá trị đã dùng để chọn tham số làm bằng chứng độc lập.
5. Chỉ sau các bước trên mới viết phần kết quả concordance trong đề cương.

Phần mở rộng climbing assay, LIF hoặc pharmacology là hướng nghiên cứu riêng,
không nên coi là đã có chỉ vì chúng xuất hiện trong DOCX. Với mục tiêu hiện tại,
pipeline computational action-level đã đủ để thực hiện pilot và thu thập
provenance đúng cách.
