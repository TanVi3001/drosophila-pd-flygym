# AI-assisted Literature Curation Workflow

## Phạm vi

Literature Assistant là một workflow hỗ trợ curator, không phải hệ thống
autonomous extraction, web crawler hay RAG. Nó chỉ đọc các file cục bộ do
người nghiên cứu cung cấp: PDF, Markdown, TXT và CSV.

Parser chỉ nhận các trường có cấu trúc rõ ràng theo dạng `key: value` hoặc
`key=value`. Văn bản tự do không được dùng để suy luận gene, genotype, assay
hay phenotype. Package này cũng không tải paper từ Internet và không gọi mô
hình AI.

## Luồng dữ liệu

```text
Local source files
        |
        v
Deterministic parser
        |
        v
CandidatePhenotype records
        |
        v
candidate_review.json
        |
        v
Human approve / reject / edit / comment
        |
        +--> review_summary.md + approved.csv + rejected.csv + pending.csv
        |
        +--> approved candidates only -> existing PhenotypeRecord model
```

`candidate_review.json` là nguồn lưu trữ của queue review. Workflow không ghi
trực tiếp `research/phenotype_atlas/phenotype_database.csv` và không tự cập
nhật Digital Phenotype Atlas.

## Candidate và provenance

Candidate có thể chứa gene, genotype, assay, age, sex, các metric vận động,
sample size, citation và các con trỏ figure/table/page. DOI được giữ để phát
hiện trùng lặp. Một candidate muốn được approve phải có provenance, assay,
figure reference và unit cho mọi metric định lượng được cung cấp. Confidence
chỉ là trường do curator nhập, không phải điểm tự động do parser tính.

## Sử dụng Python

```python
from drosophila_pd.literature_assistant import LiteratureAssistantWorkflow

workflow = LiteratureAssistantWorkflow("results/literature_review")
workflow.run(["research/papers/phenotypes.csv"])

# Chỉ curator mới quyết định trạng thái.
workflow.approve("paper_001", reviewer="name", comment="Verified against Fig. 2")
records = workflow.export_approved()
workflow.write_reports()
```

Các candidate mới luôn ở trạng thái `pending`. `edit()` quay candidate về
`pending`, vì mọi chỉnh sửa cần được approve lại. `export_approved()` chỉ trả
về các record đã được approve rõ ràng.

## Định dạng nguồn có cấu trúc

Markdown/TXT có thể chứa block như sau:

```text
[candidate]
candidate_id: paper_001
paper_id: paper_001
citation: Contract citation supplied by curator
gene: not reported
assay: locomotion assay
walking_speed: 1.2
walking_speed_unit: mm/s
figure_reference: Fig. 2
table_reference: Table 1
supplementary_reference: Supplementary Table 1
page: 4
```

CSV dùng tên cột tương ứng với candidate fields. Các cột `id`, `figure`,
`table`, `supplement`, `walking_speed_mean`, `stride_length_mean`,
`pause_fraction`, `turning_rate` và `climbing_score` có alias tường minh.

PDF cần dependency tùy chọn `pypdf`; parser chỉ trích xuất text từ file local
và vẫn yêu cầu các trường có cấu trúc. Nếu thiếu dependency hoặc PDF không
đọc được, workflow báo lỗi thay vì bỏ qua hoặc tự suy diễn.

## Kiểm tra và báo cáo

Validation phát hiện duplicate DOI, thiếu provenance, thiếu figure, thiếu
assay, thiếu unit và confidence ngoài khoảng `[0, 1]`. Báo cáo phân biệt
`approved`, `rejected` và `pending`. Các kết quả này là trạng thái quản trị
nguồn tài liệu, không phải kết luận sinh học hay chẩn đoán.
