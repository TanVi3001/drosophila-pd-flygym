# Audit artifact nghiên cứu bên ngoài

Repository có thể nhận các gói kết quả do thành viên nhóm gửi từ một branch,
một máy khác hoặc một phiên bản code khác. Gói `drosophila_pd_all_videos.zip`
được kiểm tra bằng công cụ chỉ đọc:

```powershell
python scripts/audit_external_artifacts.py `
  --archive C:\path\to\drosophila_pd_all_videos.zip `
  --output reports/external_artifact_audit
```

Công cụ không giải nén file, không chạy simulation và không đưa dữ liệu vào
pipeline khoa học. Nó ghi:

- SHA256 của archive và từng member;
- số lượng JSON, video và file khác;
- JSON có parse được không;
- report có `model`, `experiment_id`, sample count và speed hay không;
- đường dẫn nguồn bên ngoài chưa được đối chiếu;
- sự có mặt của `rollout.json`, `rollout.npz` và `viewer_pose.json`;
- đường dẫn ZIP không an toàn hoặc tên member trùng.

Video chỉ được inventory và hash, không được coi là đã được xác nhận codec,
số frame hay nội dung hình ảnh. Muốn xác minh các thuộc tính đó cần một bước
review video có công cụ phù hợp và provenance của encoder.

## Kết quả gói nhóm đã cung cấp

Archive có 15 member: 7 JSON report và 8 MP4. Các JSON đều có cấu trúc report
so sánh `baseline`/`perturbed` và trường `overall_pass=true`. Mỗi report ghi
sample count 5001, step count 5000 và timestep 0.0001 s trong phần metric.

Archive không có rollout thô (`rollout.json`, `rollout.npz`) hoặc
`viewer_pose.json`, nên không thể dùng riêng archive này để tái lập viewer.
Các report cũng tham chiếu `bridge_scales.json`/`fly-brain`, nhưng các nguồn đó
không nằm trong repository hiện tại. Vì vậy các số liệu trong archive chỉ nên
được gọi là output mô phỏng tính toán do nhóm cung cấp, chưa phải ground truth
sinh học hay bằng chứng xác nhận Parkinson.

## Quy tắc tiếp nhận

Trước khi dùng một report làm input calibration, nhóm cần bổ sung:

1. commit nguồn và manifest runtime chính xác;
2. config, seed và command tạo report;
3. rollout thô cùng checksum;
4. liên kết rõ giữa video và condition/seed, không suy ra chỉ từ tên file;
5. review thủ công các mapping literature và đơn vị metric.

Các kết quả này không tự động được nhập vào `phenotype_database.csv`.
