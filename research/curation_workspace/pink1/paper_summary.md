# Pink1 phenotype curation - candidate review

> Bản mapping phenotype sang Disease Layer nằm trong [disease_layer_mapping.md](disease_layer_mapping.md), [disease_layer_mapping.csv](disease_layer_mapping.csv) và [disease_layer_mapping.json](disease_layer_mapping.json). Mapping chỉ là giả thuyết tính toán có confidence; chưa có record nào được approve tự động.

## Phạm vi

Đây là **đợt 1: nhóm Pink1**, gồm 18 bài primary research hoặc candidate cần sàng lọc lại. Đây chưa phải systematic review và chưa phải dữ liệu đã được approve vào Phenotype Atlas.

Mục tiêu là tìm các phép đo vận động có provenance rõ để sau này xem xét calibration Disease Layer. Các số nằm trong biểu đồ nhưng chưa có source data hoặc chưa được kiểm tra chắc chắn **không được chép thành số**. Những trường đó được ghi là `pending_manual_extraction` trong `paper_information.json`.

Tình trạng nhóm: **18 candidate; 7 high-priority direct candidates; chưa có paper nào được approve tự động.** Cần người review mở full text, kiểm tra genotype/control/assay/age/sex/n/unit và trích số từ figure hoặc supplementary trước khi nhập atlas.

## Tóm tắt nhanh

| ID | Nguồn | Endpoint vận động | Mức phù hợp sơ bộ | Việc còn thiếu |
|---|---|---|---|---|
| PINK1-001 | Park et al., 2006 | Locomotive defects | ★★★★☆ | Assay và số cụ thể |
| PINK1-002 | Clark et al., 2006 | Flight muscle; locomotion chưa rõ | ★★☆☆☆ | Xác nhận assay |
| PINK1-003 | Yang et al., 2006 | Locomotion/rescue | ★★★★☆ | Số và protocol |
| PINK1-004 | Yang et al., 2008 | Behavioral phenotype | ★★★☆☆ | Metric cụ thể |
| PINK1-005 | Todd & Staveley, 2008 | Climbing/mobility | ★★★★☆ | Số và protocol |
| PINK1-006 | Tain et al., 2009 | Climbing/flight | ★★★☆☆ | Metadata đầy đủ |
| PINK1-007 | TRAP1 study, 2013 | Negative geotaxis/climbing | ★★★★★ | Giá trị trên figure |
| PINK1-008 | ref(2)P study, 2013 | Climbing | ★★★★☆ | Giá trị trên figure |
| PINK1-009 | Parkin phosphorylation, 2014 | Climbing | ★★★★☆ | Genotype và số |
| PINK1-010 | Miro study, 2014 | Crawling/climbing/flight | ★★★★☆ | Tách stage và số |
| PINK1-011 | Lee et al., 2018 | Climbing/flight phụ | ★★★☆☆ | Xác nhận endpoint |
| PINK1-012 | Cornelissen et al., 2018 | Locomotion chưa xác nhận | ★★☆☆☆ | Có thể loại |
| PINK1-013 | SOD study, 2018 | Negative geotaxis | ★★★★★ | Giá trị từ figure |
| PINK1-014 | STING study, 2020 | Climbing | ★★★★☆ | Genotype/n và số |
| PINK1-015 | Communications Biology, 2022 | Single-fly speed/trajectory | ★★★★☆ | Tách baseline/L-DOPA |
| PINK1-016 | IP3R study, 2023 | Negative geotaxis | ★★★★☆ | Giá trị và n |
| PINK1-017 | Cdk8/CDK19 study, 2024 | Climbing | ★★★★★ | Giá trị từ source data |
| PINK1-018 | Pech et al., 2024 | SING geotaxis | ★★★★☆ | Panel và số chuẩn hóa |

---

## PINK1-001 - Park et al. (2006)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/16672980/) · DOI `10.1038/nature04788` · Nature.

**Paper nghiên cứu gì?** Nhóm nghiên cứu khảo sát hậu quả của mất chức năng PINK1 ở Drosophila và mối liên hệ với Parkin. Bài báo báo cáo thoái hóa cơ bay gián tiếp, tế bào dopaminergic và khiếm khuyết vận động. Parkin có thể bổ sung một số phenotype do mất PINK1.

**Thí nghiệm:** Mô hình PINK1 loss-of-function và các điều kiện rescue bằng Parkin. Tuổi, giới tính, số mẫu và protocol vận động chưa được xác minh trong lượt này.

**Phenotype:** Có bằng chứng định tính cho `locomotive defects`. Chưa có giá trị walking speed, distance, stride, pause hoặc heading được chép.

**Hình/bảng:** Cần mở full text và figure để xác định panel, đơn vị và số mẫu.

**Đánh giá:** ★★★★☆. Phù hợp cho Disease Signature và Validation; chưa đủ để làm target số cho Calibration.

**Đề xuất:** `Disease Signature`, `Validation`. Không dùng như ngưỡng bệnh.

## PINK1-002 - Clark et al. (2006)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/16672981/) · DOI `10.1038/nature04779` · Nature.

**Paper nghiên cứu gì?** Bài báo nghiên cứu vai trò của pink1 trong chức năng ty thể và tương tác di truyền với parkin. Nội dung chính tập trung vào cơ bay, ty thể và thoái hóa mô.

**Thí nghiệm:** PINK1 loss-of-function và các phép thử tương tác với Parkin. Abstract không cung cấp đủ thông tin để xác nhận đây là dataset locomotion trực tiếp.

**Phenotype:** Có phenotype cơ bay và ty thể. Chưa ghi nhận một số đo walking/climbing có đơn vị và n rõ ràng từ phần đã kiểm tra.

**Hình/bảng:** Chưa xác định panel locomotion hợp lệ.

**Đánh giá:** ★★☆☆☆ cho mục tiêu locomotion. Nên giữ ở nhóm supporting/reference, không đưa thẳng vào calibration.

**Đề xuất:** `Chỉ tham khảo`; chỉ nâng cấp nếu full text xác nhận assay vận động định lượng.

## PINK1-003 - Yang et al. (2006)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/16818890/) · DOI `10.1073/pnas.0602493103` · PNAS.

**Paper nghiên cứu gì?** Nghiên cứu hậu quả của bất hoạt Pink1 ở ruồi và khả năng rescue bằng Parkin. Bài báo liên hệ phenotype cơ, neuron dopaminergic và vận động.

**Thí nghiệm:** Pink1 inactivation, có điều kiện Parkin rescue. Chi tiết tuổi, giới tính, số mẫu và thang đo vận động cần lấy từ full text.

**Phenotype:** Abstract/title xác nhận locomotor defect; chưa trích một con số cụ thể.

**Hình/bảng:** Cần xác định figure chứa locomotion và lấy đúng đơn vị.

**Đánh giá:** ★★★★☆. Nguồn nền tảng để xác định Disease Signature Pink1/Parkin.

**Đề xuất:** `Disease Signature`, `Validation`; chưa approve cho Calibration numeric target.

## PINK1-004 - Yang et al. (2008)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/18443288/) · DOI `10.1073/pnas.0711845105` · PNAS.

**Paper nghiên cứu gì?** Bài báo khảo sát PINK1 và động lực học phân chia/hợp nhất của ty thể. Một số điều kiện di truyền được dùng để kiểm tra liên hệ giữa ty thể và phenotype của ruồi.

**Thí nghiệm:** PINK1 mutants và perturbation bộ máy fission/fusion. Endpoint vận động cụ thể chưa được xác minh trong lượt này.

**Phenotype:** Có behavioral context nhưng chưa có số speed, distance, stride hoặc climbing được xác nhận.

**Hình/bảng:** Cần manual full-text review.

**Đánh giá:** ★★★☆☆. Hữu ích cho disease mechanism context, yếu hơn cho calibration locomotion.

**Đề xuất:** `Disease Signature`, `Chỉ tham khảo`.

## PINK1-005 - Todd & Staveley (2008)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/19088817/) · DOI `10.1139/G08-085` · Genome.

**Paper nghiên cứu gì?** Nghiên cứu tương tác giữa PINK1 và alpha-synuclein trong mô hình ruồi. Nhóm tác giả quan sát khả năng vận động và sự mất khả năng leo sớm trong các điều kiện biểu hiện alpha-synuclein.

**Thí nghiệm:** Alpha-synuclein expression kết hợp với điều chỉnh PINK1. Tuổi, giới tính và n cần xác minh.

**Phenotype:** `Premature loss of climbing ability` được nêu; chưa chép giá trị cụ thể.

**Hình/bảng:** Cần xác định panel climbing và số liệu gốc.

**Đánh giá:** ★★★★☆. Tốt cho signature tương tác PINK1-alpha-synuclein; cần tách hiệu ứng alpha-synuclein khỏi Pink1.

**Đề xuất:** `Disease Signature`, `Validation`.

## PINK1-006 - Tain et al. (2009)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/19282869/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2711053/).

**Paper nghiên cứu gì?** Nghiên cứu HtrA2 trong pathway PINK1/Parkin. Đây là bài pathway study, trong đó climbing và flight được dùng để so sánh phenotype.

**Thí nghiệm:** Các genotype liên quan HtrA2/PINK1 và điều kiện so sánh Parkin. Chi tiết tuổi, giới tính, n và protocol chưa trích đầy đủ.

**Phenotype:** Climbing defect và flight phenotype là các endpoint cần kiểm tra.

**Hình/bảng:** Các phần cần xem lại gồm Figure 7-8 và phần methods tương ứng.

**Đánh giá:** ★★★☆☆. Supporting source; không dùng trực tiếp nếu không phân biệt được HtrA2 và Pink1.

**Đề xuất:** `Disease Signature`, `Chỉ tham khảo`.

## PINK1-007 - TRAP1 rescues PINK1 loss-of-function phenotypes (2013)

**Nguồn:** [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3690968/).

**Paper nghiên cứu gì?** Nghiên cứu xem TRAP1 có rescue phenotype do mất PINK1 hay không. Bài báo nêu rõ Pink1[B9] giảm climbing và flight, và TRAP1 hoạt động có thể cải thiện climbing.

**Thí nghiệm:** Pink1[B9], Pink1 RNAi và human TRAP1 WT/ATPase-deficient. Phần method đã ghi nhận 20 ruồi đực mỗi buồng, vạch 10 cm, thời gian 20 giây, năm lần thử; tổng số tối thiểu 120 ruồi/genotype được nêu.

**Phenotype:** Climbing và flight; kết quả rescue nằm ở Figure 1E-F. Giá trị trên đồ thị chưa được transcribe.

**Thuật ngữ:** Negative geotaxis là đo số ruồi leo qua vạch sau khi bị gõ xuống.

**Đánh giá:** ★★★★★. Một trong các ứng viên tốt nhất cho calibration/validation sau khi lấy source data.

**Đề xuất:** `Calibration`, `Validation`, `Disease Signature`. Không suy ra hiệu quả điều trị.

## PINK1-008 - ref(2)P and Parkin suppression (2013)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24157867/) · [PDF/article](https://www.nature.com/articles/cddis2013394.pdf) · DOI `10.1038/cddis.2013.394`.

**Paper nghiên cứu gì?** Nghiên cứu vai trò của ref(2)P trong việc Parkin làm giảm phenotype ty thể của Pink1 mutants.

**Thí nghiệm:** Pink1 mutant kết hợp các điều kiện Parkin/ref(2)P. Bài dùng standard climbing assay.

**Phenotype:** Có climbing defect và rescue climbing liên quan ref(2)P. Phần đã kiểm tra ghi n >= 60/genotype, mean +/- SD.

**Hình/bảng:** Cần xác định panel climbing và chép giá trị theo từng genotype.

**Đánh giá:** ★★★★☆. Tốt cho signature di truyền và validation; chưa đủ numeric target.

**Đề xuất:** `Disease Signature`, `Validation`.

## PINK1-009 - PINK1 phosphorylation of Parkin (2014)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24901221/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4046931/).

**Paper nghiên cứu gì?** Nghiên cứu cách phosphorylation của Parkin bởi PINK1 ảnh hưởng hoạt tính Parkin trong ruồi.

**Thí nghiệm:** So sánh PINK1-null với Parkin WT/SA/SE; climbing và wing posture là các endpoint quan sát.

**Phenotype:** Abnormal/slower climbing và khác biệt rescue giữa các biến thể Parkin. Phần methods đã thấy thông tin 20 climbing trials; giá trị cuối chưa trích.

**Hình/bảng:** Figure 4 cần được mở và ghi panel/genotype/đơn vị.

**Đánh giá:** ★★★★☆. Hữu ích để phân biệt phenotype motor với cơ chế rescue.

**Đề xuất:** `Calibration`, `Validation`.

## PINK1-010 - PINK1 phosphorylation of Miro (2014)

**Nguồn:** [Nature](https://www.nature.com/articles/srep06962) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4223694/) · DOI `10.1038/srep06962`.

**Paper nghiên cứu gì?** Nghiên cứu PINK1/Miro ở synapse, neuron dopaminergic và khả năng vận động theo stage phát triển.

**Thí nghiệm:** Đo crawling/idling ở ấu trùng third-instar; đo climbing, jumping, flying ở ruồi trưởng thành 15 ngày.

**Phenotype:** PINK1-null làm giảm locomotor ability; phần đã kiểm tra ghi n=21-44 ở larva và n=22-119 ở adult. Không trộn hai nhóm tuổi vào cùng một target.

**Hình/bảng:** Figures 4 và 6; giá trị trên đồ thị còn chờ trích.

**Đánh giá:** ★★★★☆. Tốt cho Disease Signature theo stage, không phải walking trajectory thuần nhất.

**Đề xuất:** `Disease Signature`, `Validation`.

## PINK1-011 - Lee et al. (2018)

**Nguồn:** [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5940313/) · DOI `10.1083/jcb.201801044`.

**Paper nghiên cứu gì?** Bài tập trung vào basal mitophagy và ảnh hưởng của mất Pink1/Parkin. Locomotion/flight được dùng như behavioral validation.

**Thí nghiệm:** Pink1 B9 và parkin loss-of-function; phần method đã thấy male adults 1-3 ngày cho assay.

**Phenotype:** Chỉ giữ lại nếu full text nêu rõ assay vận động và panel. Không biến kết quả mitophagy thành motor phenotype.

**Hình/bảng:** Cần xác định figure behavioral validation.

**Đánh giá:** ★★★☆☆. Supporting source, ưu tiên thấp cho calibration.

**Đề xuất:** `Validation`, `Chỉ tham khảo`.

## PINK1-012 - Cornelissen et al. (2018)

**Nguồn:** [eLife](https://elifesciences.org/articles/35878) · DOI `10.7554/eLife.35878` · PMID `29809156`.

**Paper nghiên cứu gì?** Nghiên cứu mitophagy phụ thuộc tuổi ở Parkin và PINK1 mutant.

**Thí nghiệm:** Pink1 B9 và parkin mutants; trong lượt này chưa xác nhận được một locomotion assay định lượng có thể dùng cho atlas.

**Phenotype:** Chưa ghi số locomotion. Không nhập vào calibration nếu không tìm được assay, đơn vị và source figure.

**Hình/bảng:** Để trạng thái screening candidate.

**Đánh giá:** ★★☆☆☆ cho mục tiêu locomotion.

**Đề xuất:** `Chỉ tham khảo`; có thể loại ở vòng full-text screening.

## PINK1-013 - Superoxide dismutating molecules (2018)

**Nguồn:** [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5905640/).

**Paper nghiên cứu gì?** Nghiên cứu liệu tăng SOD/SOD2 hoặc dùng M40403 có làm thay đổi phenotype vận động do mất PINK1/Parkin không.

**Thí nghiệm:** Counter-current negative geotaxis. Ruồi đực 1-2 ngày tuổi, vạch 8 cm, thời gian 10 giây, mỗi con thử 5 lần, n > 150/genotype.

**Phenotype:** Pink1 có climbing defect; Sod2 làm giảm defect; M40403 có đáp ứng theo liều trong phạm vi được thử. Số phần trăm/mean cụ thể chưa được chép từ figure.

**Hình/bảng:** Figures 7-8, mean và 95% CI.

**Đánh giá:** ★★★★★. Assay metadata rất tốt cho calibration/validation.

**Đề xuất:** `Calibration`, `Validation`. Không gọi đây là bằng chứng hiệu quả lâm sàng.

## PINK1-014 - STING pathway (2020)

**Nguồn:** [Nature](https://www.nature.com/articles/s41598-020-59647-3) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7021792/) · DOI `10.1038/s41598-020-59647-3`.

**Paper nghiên cứu gì?** Kiểm tra STING/Relish có giải thích hoặc rescue phenotype Pink1/Parkin hay không.

**Thí nghiệm:** Pink1 B9 kết hợp Sting/Relish perturbations; assay chính là climbing.

**Phenotype:** Bài cung cấp cả kết quả không rescue/negative interaction. Đây là dữ liệu quan trọng, không được loại chỉ vì không tạo phenotype mong muốn.

**Hình/bảng:** Figure 5A; mean và 95% CI; n được hiển thị theo bar nhưng chưa transcribe.

**Đánh giá:** ★★★★☆. Tốt cho validation và negative signature.

**Đề xuất:** `Validation`, `Disease Signature`.

## PINK1-015 - L-DOPA and Drosophila behavioral analyses (2022)

**Nguồn:** [Communications Biology](https://www.nature.com/articles/s42003-022-03830-x) · DOI `10.1038/s42003-022-03830-x`.

**Paper nghiên cứu gì?** Nghiên cứu các gene liên quan levodopa-induced dyskinesia và dùng phân tích hành vi ở ruồi.

**Thí nghiệm:** PINK1 B9/RV, acute/chronic L-DOPA, single-fly trajectory, speed và abnormal involuntary movement (AIM) score.

**Phenotype:** Có speed, trajectory và AIM. N=6 được ghi nhận cho một tập trajectory; N=10-12 cho một số AIM analyses. Phải tách baseline, L-DOPA và AIM.

**Hình/bảng:** Figure 3B-H và Supplementary Figures 2-3.

**Đánh giá:** ★★★★☆. Tiềm năng cao cho trajectory-based validation, nhưng không dùng drug-response để gán thẳng Disease Layer baseline.

**Đề xuất:** `Calibration`, `Validation` sau khi phân tầng điều kiện.

## PINK1-016 - PINK1/Parkin and IP3R (2023)

**Nguồn:** [Nature Communications](https://www.nature.com/articles/s41467-023-40929-z) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10457342/) · DOI `10.1038/s41467-023-40929-z`.

**Paper nghiên cứu gì?** Nghiên cứu PINK1/Parkin và giải phóng calcium từ ER qua IP3R.

**Thí nghiệm:** Có negative geotaxis/climbing. Method đã ghi ruồi đực 3 ngày, vial 18 cm, vạch 15 cm, 3 trial/group trong 10 thí nghiệm độc lập.

**Phenotype:** Có climbing endpoint trong bối cảnh PINK1/Parkin; giá trị cụ thể chưa chép.

**Hình/bảng:** Cần lấy đúng panel và n theo genotype.

**Đánh giá:** ★★★★☆. Tốt cho validation phụ trợ; endpoint locomotion không phải trọng tâm chính.

**Đề xuất:** `Validation`, `Disease Signature`.

## PINK1-017 - Cdk8/CDK19 (2024)

**Nguồn:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/38637532/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11026413/).

**Paper nghiên cứu gì?** Nghiên cứu Cdk8/CDK19, Drp1 và khả năng làm giảm phenotype Pink1 deficiency.

**Thí nghiệm:** Pink1 B9 với RFP/hPink1/Cdk8 hoặc CDK19 variants; đo climbing và thorax indentation.

**Phenotype:** Figure 8b có n=80/74/65; Figure 8c có n=56/71/98. Ruồi 3 ngày; một assay được nuôi ở 29 C. Kết quả định lượng trên violin plot chưa transcribe.

**Hình/bảng:** Figure 8B-C; mean +/- SD.

**Đánh giá:** ★★★★★. Ứng viên trực tiếp mạnh vì metadata assay và sample size rõ.

**Đề xuất:** `Calibration`, `Validation`; cần xác minh journal/DOI và lấy source data trước khi approve.

## PINK1-018 - Pech et al. (2024)

**Nguồn:** [eLife](https://elifesciences.org/articles/98348) · [Figures](https://elifesciences.org/articles/98348/figures) · DOI `10.7554/eLife.98348`.

**Paper nghiên cứu gì?** Nghiên cứu rối loạn synapse ở nhiều mô hình Parkinsonism fly, trong đó có PINK1.

**Thí nghiệm:** Startle-induced negative geotaxis (SING) ở 5 +/- 1 ngày và 25 +/- 1 ngày; khoảng 95% pink1 mutants chết trước 25 ngày nên có nhóm được test ở 15 ngày.

**Phenotype:** Age-dependent geotaxis performance và survival context. Figure 1B dùng normalized-to-control, mean +/- SEM; n >= 5 trong mô tả đã xem.

**Hình/bảng:** Figure 1B; cần lấy numeric values và denominator chính xác.

**Đánh giá:** ★★★★☆. Tốt cho signature theo tuổi, nhưng không phải walking/stride trajectory liên tục.

**Đề xuất:** `Disease Signature`, `Validation`.

## Thuật ngữ dùng trong nhóm Pink1

- **Locomotion:** khả năng di chuyển của ruồi.
- **Climbing / negative geotaxis:** sau khi gõ ruồi xuống đáy, đo số ruồi leo qua một vạch trong thời gian định trước.
- **Flight assay:** kiểm tra khả năng bay; không đồng nhất với walking speed.
- **Crawling:** di chuyển của ấu trùng; không gộp trực tiếp với dữ liệu ruồi trưởng thành.
- **SING:** startle-induced negative geotaxis, một dạng đo phản ứng leo sau kích thích.
- **PINK1 loss-of-function:** giảm hoặc mất chức năng gene PINK1 trong mô hình ruồi; đây không tự động đồng nghĩa với chẩn đoán Parkinson.
- **Rescue:** một can thiệp di truyền hoặc phân tử làm phenotype đo được thay đổi theo hướng gần control trong thí nghiệm đó.
- **AIM score:** abnormal involuntary movement score; chỉ dùng trong đúng bối cảnh assay và treatment của paper.
- **n:** số đơn vị mẫu được phân tích; cần phân biệt số ruồi, số trial và số experiment độc lập.

## Kết luận curation của nhóm

1. Nhóm Pink1 có nhiều nguồn primary research về climbing, flight, geotaxis và một số trajectory.
2. Các bài có method/sample-size rõ nhất trong lượt này là PINK1-007, PINK1-010, PINK1-013, PINK1-015, PINK1-016 và PINK1-017.
3. Chưa có giá trị numeric nào được approve tự động vào Phenotype Atlas.
4. Không thể quy đổi climbing, flight, crawling và continuous walking thành cùng một metric nếu chưa có bước harmonization được nhóm nghiên cứu phê duyệt.
5. Paper dùng intervention/rescue chỉ cho biết response trong điều kiện thí nghiệm; không được diễn giải thành hiệu quả thuốc hoặc giá trị lâm sàng.
6. Sau khi nhóm review, cần hoàn tất full-text extraction, figure/source-data transcription, duplicate check và approval từng candidate.

## Bước review thủ công tiếp theo

- [ ] Xác minh author list, journal, DOI/PMID của các dòng còn thiếu.
- [ ] Mở full text cho PINK1-001 đến PINK1-018.
- [ ] Điền age, sex, genotype, control, temperature, assay duration và sample unit.
- [ ] Chụp lại figure/table reference chính xác.
- [ ] Chỉ ghi numeric value khi đọc chắc chắn từ text/table/source data.
- [ ] Tách baseline, rescue, drug exposure và negative-result conditions.
- [ ] Reviewer ký `approve`, `reject` hoặc `edit` trong workspace; chỉ record đã approve mới được đưa sang Phenotype Atlas.

## Nguồn chính đã dùng

- [Park et al. 2006 - PubMed](https://pubmed.ncbi.nlm.nih.gov/16672980/)
- [Clark et al. 2006 - PubMed](https://pubmed.ncbi.nlm.nih.gov/16672981/)
- [Yang et al. 2006 - PubMed](https://pubmed.ncbi.nlm.nih.gov/16818890/)
- [Yang et al. 2008 - PubMed](https://pubmed.ncbi.nlm.nih.gov/18443288/)
- [Todd & Staveley 2008 - PubMed](https://pubmed.ncbi.nlm.nih.gov/19088817/)
- [TRAP1 study - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3690968/)
- [SOD/SOD2 study - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5905640/)
- [STING study - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7021792/)
- [Cdk8/CDK19 study - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11026413/)
- [PINK1/Parkin-IP3R study - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10457342/)
- [PINK1 locomotion/SING study - eLife](https://elifesciences.org/articles/98348)
