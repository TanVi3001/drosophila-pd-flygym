# Mapping Pink1 phenotype sang Disease Layer

## Cách hiểu tài liệu

Tài liệu này nối bốn lớp thông tin:

```text
Paper
  ↓
Phenotype quan sát được
  ↓
Disease Signature
  ↓
Proxy tính toán có thể liên quan
  ↓
Calibration hoặc Validation candidate
```

Mapping không phải kết luận rằng proxy đó là cơ chế sinh học thật. Confidence chỉ nói mức hợp lý của mối liên hệ trong phạm vi dữ liệu paper đã cung cấp. Nếu paper không có số, ghi rõ: **Không có số liệu định lượng.** Nếu chưa đủ bằng chứng, ghi: **Không đủ bằng chứng.**

Các proxy được xem xét: `motor_vigor`, `coordination`, `delay`, `noise`, `fatigue`, `asymmetry`, `freezing`, `latency`, `postural_instability`.

## PINK1-001 - Park et al. (2006)

**Paper:** *Mitochondrial dysfunction in Drosophila PINK1 mutants is complemented by parkin*. Nature. DOI `10.1038/nature04788`; PMID `16672980`. [Nguồn PubMed](https://pubmed.ncbi.nlm.nih.gov/16672980/)

**Phenotype được ghi nhận:** Paper báo cáo locomotive defects trong PINK1 loss-of-function, cùng với phenotype cơ và neuron dopaminergic. Trong bộ hồ sơ hiện tại, **không có số liệu định lượng** cho walking speed, climbing success, pause hoặc stride đã được xác minh.

**Mapping chính:**

- `motor_vigor`: **HIGH**. Locomotion tổng thể giảm có thể được biểu diễn trước hết bằng motor output thấp hơn.
- `coordination`: **LOW**. Có thể liên quan, nhưng paper chưa cung cấp gait hoặc inter-leg timing để kiểm tra.
- Các proxy delay, noise, fatigue, asymmetry, freezing, latency và postural instability: **Không đủ bằng chứng**.

**Calibration:** Conditional. Có thể dùng locomotion làm target sau khi trích exact assay, đơn vị, tuổi, giới tính, control và sample size.

**Validation:** Có thể dùng để kiểm tra hướng phenotype và rescue bởi Parkin nếu full text được trích đầy đủ.

**Giải thích dễ hiểu:** Paper cho thấy khi PINK1 bị mất chức năng, ruồi có vấn đề về vận động. Trong mô hình FlyGym, điều này có thể gợi ý giảm `motor_vigor`, nhưng không có nghĩa neuron bị mô phỏng trực tiếp hay đã chứng minh đây là Parkinson sinh học.

## PINK1-002 - Clark et al. (2006)

**Paper:** *Drosophila pink1 is required for mitochondrial function and interacts genetically with parkin*. Nature. DOI `10.1038/nature04779`; PMID `16672981`. [Nguồn PubMed](https://pubmed.ncbi.nlm.nih.gov/16672981/)

**Phenotype được ghi nhận:** Bài tập trung vào chức năng ty thể, cơ bay và tương tác di truyền với Parkin. Trong lượt curation này, locomotion endpoint định lượng chưa được xác nhận. **Không có số liệu định lượng đủ chắc chắn** cho Disease Layer.

**Mapping:**

- `UNMAPPED`: **NONE** cho calibration locomotion.
- `postural_instability`: chỉ là khả năng **LOW** nếu full text chứng minh phenotype tư thế/cơ bay ảnh hưởng hành vi.
- Các proxy khác: **Không đủ bằng chứng**.

**Calibration:** Không nên dùng trực tiếp.

**Validation:** Chỉ nên giữ làm tài liệu supporting cho quan hệ PINK1/Parkin và mitochondrial phenotype.

**Giải thích dễ hiểu:** Bài này giúp hiểu bối cảnh sinh học của PINK1, nhưng không nên biến mọi kết quả về ty thể thành một tham số motor. Cần một assay vận động rõ ràng trước khi map.

## PINK1-003 - Yang et al. (2006)

**Paper:** *Mitochondrial pathology and muscle and dopaminergic neuron degeneration caused by inactivation of Drosophila Pink1 is rescued by Parkin*. PNAS. DOI `10.1073/pnas.0602493103`; PMID `16818890`. [Nguồn PubMed](https://pubmed.ncbi.nlm.nih.gov/16818890/)

**Phenotype:** Locomotor defect, muscle degeneration và rescue bởi Parkin. **Không có số liệu định lượng đã được xác minh trong lượt này.**

**Mapping:**

- `motor_vigor`: **HIGH**, vì locomotor defect là endpoint trực tiếp.
- `postural_instability`: **LOW**, vì muscle degeneration có thể ảnh hưởng tư thế nhưng chưa phải phép đo tư thế.
- `coordination`: **LOW**, chỉ là khả năng phụ nếu full text có gait/flight detail.

**Calibration:** Conditional với metric locomotion, sau khi lấy số và protocol.

**Validation:** Có thể dùng điều kiện Parkin rescue để kiểm tra model có thay đổi theo hướng paper hay không.

**Giải thích:** Paper gợi ý rằng ruồi PINK1 có khiếm khuyết vận động và Parkin có thể rescue trong điều kiện thí nghiệm. Trong FlyGym, ta có thể kiểm tra motor vigor reduction trước; không được nói Parkin đã được mô phỏng như một thuốc.

## PINK1-004 - Yang et al. (2008)

**Paper:** *Pink1 regulates mitochondrial dynamics through interaction with the fission/fusion machinery*. PNAS. DOI `10.1073/pnas.0711845105`; PMID `18443288`. [Nguồn PubMed](https://pubmed.ncbi.nlm.nih.gov/18443288/)

**Phenotype:** Có behavioral context liên quan Pink1 và mitochondrial fission/fusion. Metric locomotion cụ thể chưa được xác minh. **Không có số liệu định lượng đủ chắc chắn.**

**Mapping:** `UNMAPPED`, confidence **NONE** cho calibration. Không được tự chuyển mitochondrial dynamics thành `motor_vigor`, `noise` hay `fatigue`.

**Calibration:** Không dùng ở trạng thái hiện tại.

**Validation:** Có thể giữ làm supporting mechanism paper, sau khi full text xác nhận có assay locomotion.

**Giải thích:** Biết ty thể bị ảnh hưởng chưa đủ để biết ruồi đi chậm vì vigor, phối hợp hay tư thế. Cần endpoint hành vi rõ trước khi kết nối với Disease Layer.

## PINK1-005 - Todd và Staveley (2008)

**Paper:** *Pink1 suppresses alpha-synuclein-induced phenotypes in a Drosophila model of Parkinson's disease*. Genome. DOI `10.1139/G08-085`; PMID `19088817`. [Nguồn PubMed](https://pubmed.ncbi.nlm.nih.gov/19088817/)

**Phenotype:** Premature loss of climbing ability trong bối cảnh alpha-synuclein và PINK1. **Không có số liệu định lượng đã xác minh.**

**Mapping:**

- `motor_vigor`: **HIGH**, vì climbing là output vận động rõ.
- `coordination`: **LOW**, vì leo cần phối hợp chân nhưng paper không tách biến này.
- `freezing`, `latency`, `fatigue`, `asymmetry`: **Không đủ bằng chứng**.

**Calibration:** Conditional với climbing success hoặc climbing performance.

**Validation:** Có thể dùng để kiểm tra tương tác PINK1-alpha-synuclein, nhưng không gộp thành phenotype Pink1 thuần.

**Giải thích:** Paper cho thấy khả năng leo mất sớm trong điều kiện cụ thể. Điều đó gợi ý motor vigor thấp hơn; chưa nói ruồi có một bệnh tương đương người.

## PINK1-006 - Tain et al. (2009)

**Paper:** *Drosophila HtrA2 is dispensable for apoptosis but acts downstream of PINK1 independently from Parkin*. PMID `19282869`. [PubMed](https://pubmed.ncbi.nlm.nih.gov/19282869/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2711053/)

**Phenotype:** Climbing defect và flight phenotype trong các so sánh PINK1/HtrA2/Parkin. **Không có số liệu định lượng đã được chép.**

**Mapping:**

- `motor_vigor`: **HIGH** cho climbing.
- `coordination`: **MEDIUM** cho flight vì flight cần phối hợp cánh-thân.
- `postural_instability`: **LOW** nếu không có wing posture hoặc orientation assay.

**Calibration:** Conditional, nhưng phải tách hiệu ứng HtrA2 khỏi hiệu ứng Pink1.

**Validation:** Có thể dùng để kiểm tra pathway-associated phenotype.

**Giải thích:** Một paper pathway có thể chứa nhiều genotype. Không được lấy toàn bộ kết quả của HtrA2 rồi gắn trực tiếp vào Pink1 Disease Layer.

## PINK1-007 - TRAP1 rescue study (2013)

**Paper:** *TRAP1 rescues PINK1 loss-of-function phenotypes*. [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3690968/)

**Phenotype:** Pink1[B9] giảm climbing và flight; abnormal wing posture và thorax indentation. Phần phương pháp đã ghi nhận 20 ruồi đực mỗi buồng, vạch 10 cm, 20 giây, năm trial; tổng số tối thiểu 120 ruồi/genotype. Giá trị trên Figure 1E-F **chưa được trích thành số**.

**Mapping:**

- `motor_vigor`: **HIGH** cho climbing.
- `coordination`: **MEDIUM** cho flight.
- `postural_instability`: **HIGH** cho abnormal wing posture/thorax indentation.

**Calibration:** Conditional với climbing success, flight ability và posture frequency.

**Validation:** Mạnh, vì có condition rescue bằng TRAP1 WT và đối chứng ATPase-deficient.

**Giải thích:** Đây là ứng viên tốt vì paper vừa có hành vi vừa có rescue. Tuy vậy rescue trong ruồi chỉ là kết quả của thí nghiệm đó, không phải bằng chứng một phương pháp điều trị.

## PINK1-008 - ref(2)P study (2013)

**Paper:** *Drosophila ref(2)P is required for the parkin-mediated suppression of mitochondrial dysfunction in pink1 mutants*. DOI `10.1038/cddis.2013.394`; PMID `24157867`. [Nguồn](https://pubmed.ncbi.nlm.nih.gov/24157867/)

**Phenotype:** Climbing defect và climbing rescue trong điều kiện Parkin/ref(2)P. Phần đã kiểm tra ghi n >= 60/genotype, mean +/- SD. Giá trị cụ thể **chưa được trích**.

**Mapping:** `motor_vigor` **HIGH**. Không có bằng chứng đủ để gán delay, fatigue hoặc freezing.

**Calibration:** Conditional với climbing success.

**Validation:** Có, vì thiết kế rescue có thể kiểm tra hướng thay đổi của mô hình.

**Giải thích:** Climbing là metric tổng hợp. Có thể dùng nó để kiểm tra model có giảm vận động hay không, nhưng chưa thể biết thành phần nào là nguyên nhân.

## PINK1-009 - PINK1 phosphorylation of Parkin (2014)

**Paper:** *PINK1-mediated phosphorylation of Parkin boosts Parkin activity in Drosophila*. PMID `24901221`. [PubMed](https://pubmed.ncbi.nlm.nih.gov/24901221/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4046931/)

**Phenotype:** Slower/abnormal climbing và wing posture trong PINK1-null với Parkin variants. **Không có số liệu định lượng đã xác minh.**

**Mapping:**

- `motor_vigor`: **HIGH** cho climbing.
- `postural_instability`: **HIGH** cho wing posture.
- `coordination`: **LOW**, vì chưa có joint/gait decomposition.

**Calibration:** Conditional với climbing và posture.

**Validation:** Có thể dùng để kiểm tra variant-specific rescue.

**Giải thích:** Đây là ví dụ cho thấy cùng một paper có thể cung cấp hai phenotype khác nhau: một về output vận động, một về tư thế.

## PINK1-010 - PINK1/Miro study (2014)

**Paper:** *PINK1-mediated phosphorylation of Miro inhibits synaptic growth and protects dopaminergic neurons in Drosophila*. DOI `10.1038/srep06962`. [Nature](https://www.nature.com/articles/srep06962) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4223694/)

**Phenotype:** Diminished larval crawling, idling và adult climbing/jumping/flying defects. Phần đã kiểm tra ghi larval n=21-44 và adult n=22-119. **Giá trị đo cụ thể chưa được trích.**

**Mapping:**

- `motor_vigor`: **HIGH** cho crawling và adult locomotor output.
- `coordination`: **MEDIUM** cho crawling/jumping/flight.
- `freezing`: **LOW** cho idling; idling chưa đủ để định nghĩa freezing.

**Calibration:** Conditional, phải tách larval và adult, không gộp thành một target.

**Validation:** Có, vì có nhiều stage và assay.

**Giải thích:** Ấu trùng bò và ruồi trưởng thành leo là hai hành vi khác nhau. Không đưa chúng vào cùng một phân phối speed.

## PINK1-011 - Lee et al. (2018)

**Paper:** *Basal mitophagy is widespread in Drosophila but minimally affected by loss of Pink1 or parkin*. DOI `10.1083/jcb.201801044`. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5940313/)

**Phenotype:** Climbing/flight được dùng như behavioral validation. Method ghi adult male 1-3 ngày. **Không có số liệu định lượng đã được chép.**

**Mapping:** `motor_vigor` **HIGH** cho endpoint climbing/flight. Không map mitophagy trực tiếp sang Disease Layer motor.

**Calibration:** Conditional và ưu tiên thấp vì locomotion là endpoint phụ.

**Validation:** Có thể dùng để kiểm tra model ở một nguồn độc lập.

**Giải thích:** Paper chính nói về mitophagy. Chỉ lấy phần vận động khi figure và methods nêu rõ assay.

## PINK1-012 - Cornelissen et al. (2018)

**Paper:** *Deficiency of parkin and PINK1 impairs age-dependent mitophagy in Drosophila*. DOI `10.7554/eLife.35878`; PMID `29809156`. [eLife](https://elifesciences.org/articles/35878)

**Phenotype:** Trong lượt curation này chưa xác nhận được named locomotion assay đủ dùng cho atlas. **Không đủ bằng chứng.**

**Mapping:** `UNMAPPED`, confidence **NONE**.

**Calibration:** Không dùng.

**Validation:** Chưa dùng cho locomotion. Có thể loại sau full-text screening.

**Giải thích:** Không phải paper nào có PINK1 cũng là paper phenotype vận động. Giữ lại ở danh sách screening để tránh bỏ sót, nhưng không ép map.

## PINK1-013 - Superoxide dismutating molecules (2018)

**Paper:** *Superoxide dismutating molecules rescue the toxic effects of PINK1 and parkin loss*. [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5905640/)

**Phenotype:** Negative geotaxis climbing defect ở Pink1. Method ghi ruồi đực 1-2 ngày, vạch 8 cm, 10 giây, mỗi con thử 5 lần, n > 150/genotype. SOD2 làm giảm climbing defect; M40403 là intervention context. Exact mean/CI **chưa được trích từ Figure 7-8**.

**Mapping:**

- `motor_vigor`: **HIGH**.
- `postural_instability`: **LOW**, vì assay có thể chịu ảnh hưởng tư thế nhưng không đo riêng.
- `noise`, `fatigue`, `asymmetry`, `freezing`: **Không đủ bằng chứng**.

**Calibration:** Conditional với climbing success.

**Validation:** Mạnh vì có baseline và response conditions.

**Giải thích:** Paper cho ta một cách đo rõ khả năng leo. Nó không cho phép kết luận SOD2 là thuốc Parkinson; chỉ cho thấy output hành vi thay đổi trong mô hình thí nghiệm.

## PINK1-014 - STING pathway (2020)

**Paper:** *The STING pathway does not contribute to behavioural or mitochondrial phenotypes in Drosophila Pink1/parkin or mtDNA mutator models*. DOI `10.1038/s41598-020-59647-3`. [Nature](https://www.nature.com/articles/s41598-020-59647-3) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7021792/)

**Phenotype:** Pink1 climbing defect; Relish manipulation không rescue hoặc có thể làm defect nặng hơn. Figure 5A có mean/95% CI; **giá trị số chưa được chép**.

**Mapping:** `motor_vigor` **HIGH** cho Pink1 climbing defect. Không tạo proxy mới từ kết quả STING âm tính.

**Calibration:** Conditional nếu genotype mapping và values đầy đủ.

**Validation:** Mạnh cho negative-result validation.

**Giải thích:** Một kết quả “không rescue” vẫn quan trọng. Model không nên thêm STING-like proxy chỉ vì paper đã kiểm tra STING.

## PINK1-015 - L-DOPA behavioral analysis (2022)

**Paper:** *Discovery of levodopa-induced dyskinesia-associated genes using genomic studies in patients and Drosophila behavioral analyses*. Communications Biology. DOI `10.1038/s42003-022-03830-x`. [Nguồn Nature](https://www.nature.com/articles/s42003-022-03830-x)

**Phenotype:** PINK1B9 không L-DOPA có movement và speed chậm hơn revertant. L-DOPA kéo dài gây abrupt acceleration, directional change và AIM score. Paper mô tả cách tính AIM từ instantaneous speed so với mean speed; các giá trị cụ thể **chưa được nhập**.

**Mapping:**

- `motor_vigor`: **HIGH** cho untreated PINK1B9 speed/trajectory.
- `noise`: **MEDIUM** cho irregular acceleration trong treatment context.
- `coordination`: **LOW** cho directional change.
- `asymmetry`, `freezing`, `fatigue`: **Không đủ bằng chứng**.

**Calibration:** Conditional với mean speed, trajectory và AIM; phải tách baseline khỏi L-DOPA.

**Validation:** Mạnh cho time-series/trajectory validation.

**Giải thích:** Đây là paper có giá trị vì có trajectory. Nhưng chuyển động bất thường sau thuốc không được dùng làm phenotype baseline của Disease Layer.

## PINK1-016 - PINK1/Parkin and IP3R (2023)

**Paper:** *PINK1 and Parkin regulate IP3R-mediated ER calcium release*. Nature Communications. DOI `10.1038/s41467-023-40929-z`. [Nature](https://www.nature.com/articles/s41467-023-40929-z) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10457342/)

**Phenotype:** Climbing time. Methods ghi 10 ruồi đực 3 ngày trong vial 18 cm, vạch 15 cm, ba trial/group và mười experiment độc lập. **Giá trị theo genotype chưa được trích.**

**Mapping:**

- `motor_vigor`: **HIGH**, vì thời gian tới vạch là output tổng hợp.
- `latency`: **LOW**, vì completion time không tách được thời gian bắt đầu.

**Calibration:** Conditional với climbing time.

**Validation:** Có, nhất là để kiểm tra cùng hướng phenotype trên một assay khác.

**Giải thích:** Không được fit `latency` riêng chỉ từ tổng thời gian climbing. Muốn làm vậy cần event timestamp hoặc video frame-level.

## PINK1-017 - Cdk8/CDK19 study (2024)

**Paper:** *Cdk8/CDK19 promotes mitochondrial fission through Drp1 phosphorylation and can phenotypically suppress pink1 deficiency in Drosophila*. PMID `38637532`. [PubMed](https://pubmed.ncbi.nlm.nih.gov/38637532/) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11026413/)

**Phenotype:** Climbing defect và thorax indentation. Figure 8B có n=80/74/65; Figure 8C có n=56/71/98. Ruồi 3 ngày; một assay nuôi ở 29 C. **Giá trị trên violin plot chưa được trích.**

**Mapping:**

- `motor_vigor`: **HIGH** cho climbing.
- `postural_instability`: **HIGH** cho thorax indentation.
- `coordination`: **LOW**, chưa có gait data.

**Calibration:** Conditional với climbing và thorax indentation frequency.

**Validation:** Mạnh vì có hPink1/Cdk8/CDK19 rescue conditions.

**Giải thích:** Bài này có metadata tốt, nhưng cần giữ hai outcome riêng: climbing là hành vi; thorax indentation là hình thái.

## PINK1-018 - Pech et al. (2024)

**Paper:** *Synaptic deregulation of cholinergic projection neurons causes olfactory dysfunction across five fly Parkinsonism models*. eLife. DOI `10.7554/eLife.98348`; PMID `40178224`. [eLife](https://elifesciences.org/articles/98348)

**Phenotype:** Startle-induced negative geotaxis ở 5 +/- 1 ngày và 25 +/- 1 ngày; phần mô tả cho biết nhiều Pink1 mutants chết trước 25 ngày nên có nhóm được test ở 15 ngày. Figure 1B dùng normalized control, mean +/- SEM. **Không có số cụ thể đã nhập.**

**Mapping:**

- `motor_vigor`: **HIGH** cho SING/geotaxis.
- `fatigue`: **LOW**, vì age-dependent decline không tự động là fatigue trong một phiên.
- `freezing`, `delay`, `latency`: **Không đủ bằng chứng**.

**Calibration:** Conditional như age-stratified geotaxis target, không phải walking/stride target.

**Validation:** Có, vì có nhóm tuổi và normalized control.

**Giải thích:** Đây là nguồn tốt để xem thay đổi theo tuổi, nhưng không nên biến survival hoặc age effect thành một tham số fatigue mà paper chưa đo.

## Tổng hợp theo proxy

| Proxy | Bằng chứng Pink1 hiện tại | Confidence tổng quát | Ghi chú |
|---|---|---|---|
| Motor vigor | Climbing, flight, crawling, speed, geotaxis | Cao | Proxy được hỗ trợ nhiều nhất |
| Coordination | Flight, crawling, directional change | Thấp-trung bình | Chưa có nhiều joint/gait data |
| Delay | Hầu như chưa có | Thấp | Không suy ra từ completion time |
| Noise | Chủ yếu AIM/irregular acceleration trong L-DOPA | Trung bình có điều kiện | Không gán vào baseline tự động |
| Fatigue | Chưa có assay trong một phiên đủ rõ | Thấp | Age decline không đồng nghĩa fatigue |
| Asymmetry | Chưa thấy left-right metric | Không đủ bằng chứng | Không bật proxy |
| Freezing | Idling là gợi ý yếu | Thấp | Cần pause duration và threshold |
| Latency | Chỉ gợi ý từ climbing time | Thấp | Cần event timestamps |
| Postural instability | Wing posture, thorax indentation | Cao cho phenotype hình thái | Không đồng nhất orientation variance |

## Kết luận khoa học có giới hạn

Nhóm Pink1 hiện cung cấp bằng chứng mạnh nhất cho hai hướng computational proxy: `motor_vigor` và, trong các paper có wing/thorax phenotype, `postural_instability`. `coordination` có thể liên quan nhưng thường chỉ ở confidence thấp hoặc trung bình vì climbing/flight chưa được phân rã thành joint-level metrics. `noise` chỉ có ứng viên rõ trong bối cảnh trajectory và L-DOPA của PINK1-015.

Không có cơ sở để nói Pink1 xác nhận một disease layer duy nhất, cũng không có cơ sở để gọi các proxy này là neuron hoặc biomarker lâm sàng. Đây là các mapping candidates chờ calibration và validation.

## Bước tiếp theo

- [ ] Reviewer mở full text và source data của từng candidate.
- [ ] Điền numeric values, unit, uncertainty, age, sex, genotype, control.
- [ ] Tách assay theo larva/adult, walking/climbing/flight/geotaxis.
- [ ] Approve hoặc reject từng mapping.
- [ ] Chỉ sau approval mới tạo calibration target database.
- [ ] Chưa chuyển sang nhóm Parkin cho tới khi nhóm Pink1 được review.
