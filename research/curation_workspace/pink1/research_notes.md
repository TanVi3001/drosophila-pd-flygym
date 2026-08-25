# Ghi chú nghiên cứu - Mapping Pink1 vào Disease Layer

## Mục đích

File này giải thích cách đọc bộ mapping Pink1 cho thành viên mới của nhóm. Mục tiêu không phải nói rằng ruồi trong paper là một mô hình Parkinson sinh học hoàn chỉnh. Mục tiêu là hỏi một câu hẹp hơn:

> Endpoint vận động mà paper đo được có thể gợi ý thay đổi nào trong một lớp perturbation tính toán của FlyGym?

Disease Layer hiện tại là lớp thay đổi motor output đặt giữa healthy controller và simulation. Các tham số như `motor_vigor`, `coordination` hoặc `noise` là computational proxy. Chúng không phải neuron, dopamine, gene expression hoặc cơ chế tế bào.

## Cách đọc một mapping record

Mỗi record trong `disease_layer_mapping.json` có sáu phần:

1. **Paper:** nguồn và định danh bài báo.
2. **Phenotypes:** paper thực sự quan sát hoặc mô tả gì.
3. **Disease signature:** những dấu hiệu vận động có thể giữ lại cho atlas.
4. **Disease Layer mapping:** proxy có khả năng liên quan, confidence và lý do.
5. **Calibration:** có thể trở thành target số hay chưa.
6. **Validation:** có thể dùng để kiểm tra xu hướng hoặc điều kiện rescue hay chưa.

Nếu `quantitative_data` là `false`, điều đó có nghĩa là bộ curation hiện tại chưa chép một số đo đã xác minh. Không được lấy vị trí trên biểu đồ rồi tự đọc thành con số khi chưa có source data hoặc figure review.

## Ý nghĩa các proxy

### Motor vigor

Đây là proxy cho mức output vận động tổng thể. Nếu paper cho thấy ruồi leo chậm hơn, đi chậm hơn hoặc bay kém hơn, `motor_vigor` thường là mapping gần nhất. Tuy nhiên climbing còn phụ thuộc tư thế và phối hợp, nên không phải lúc nào cũng được phép kết luận chỉ có một proxy.

Ví dụ: PINK1-007, PINK1-013 và PINK1-017 đều có endpoint climbing rõ. Vì vậy `motor_vigor` được đánh giá HIGH. Muốn calibration thật vẫn phải có giá trị, đơn vị, control, tuổi, giới tính và sample structure.

### Coordination

Coordination nói về việc nhiều bộ phận cùng tạo ra chuyển động ổn định. Flight, crawling, jumping hoặc turning có thể liên quan coordination. Nhưng nếu paper chỉ báo cáo một tỷ lệ climbing thành công thì chưa thể tách coordination khỏi sức vận động tổng thể.

Vì vậy nhiều mapping coordination trong nhóm Pink1 chỉ có MEDIUM hoặc LOW. Không được dùng chúng như target độc lập nếu paper không có gait, inter-leg timing, stride hoặc joint-level measurement.

### Delay và latency

Hai proxy này liên quan đến thời gian bắt đầu hoặc thời gian phản ứng. Một climbing time dài không tự động chứng minh movement initiation delay. Nó có thể do speed, posture, coordination hoặc nhiều yếu tố cùng lúc.

Trong nhóm Pink1 hiện tại, các record gắn với `latency` đều LOW hoặc conditional. Cần video/event timestamps để tăng confidence.

### Noise

Noise là biến thiên bất thường của action hoặc trajectory. PINK1-015 có trajectory và AIM analysis trong bối cảnh L-DOPA. Đó là ứng viên cho noise trong **điều kiện treatment cụ thể**, không phải bằng chứng rằng baseline Pink1 luôn có motor noise cao.

### Fatigue

Fatigue yêu cầu bằng chứng suy giảm theo thời gian hoạt động hoặc qua các đoạn liên tiếp trong cùng protocol. Tuổi cao, lifespan ngắn hoặc nhóm già hơn không tự động là fatigue. PINK1-018 có age-dependent geotaxis, nhưng mapping fatigue được giữ LOW để tránh diễn giải quá mức.

### Asymmetry

Asymmetry cần số liệu trái-phải hoặc so sánh hai bên. Trong 18 candidate Pink1 hiện tại chưa có evidence rõ cho left-right asymmetry. Không thêm proxy này chỉ vì phenotype tổng thể không đều.

### Freezing

Freezing phải có định nghĩa rõ: khoảng dừng, ngưỡng vận tốc và thời lượng. `Idling` trong PINK1-010 có thể gợi ý dừng, nhưng chưa đủ để gọi freezing. Vì vậy mapping chỉ để LOW và cần manual review.

### Postural instability

Proxy này phù hợp hơn với abnormal wing posture, thorax indentation hoặc orientation instability. PINK1-007, PINK1-009 và PINK1-017 có phenotype hình thái liên quan, nhưng không được thay thế bằng orientation variance nếu paper không đo orientation trajectory.

## Vì sao một phenotype có nhiều mapping?

Một phép đo như climbing success là kết quả cuối của nhiều thành phần. Ruồi phải tạo lực, phối hợp chân, giữ tư thế và bắt đầu hành động. Vì vậy mapping đúng không phải là chọn một đáp án tuyệt đối mà là ghi một danh sách giả thuyết có confidence.

Ví dụ:

```text
Climbing giảm
  -> motor_vigor: HIGH
  -> coordination: LOW hoặc MEDIUM
  -> postural_instability: LOW nếu paper có wing/thorax phenotype
  -> delay: chưa đủ bằng chứng
  -> fatigue: chưa đủ bằng chứng
```

Sau đó calibration engine mới kiểm tra các giả thuyết bằng dữ liệu mô phỏng và target đã approve. Mapping không tự quyết định tham số cuối cùng.

## Calibration candidate và validation candidate

`calibration_candidate=conditional` nghĩa là paper có endpoint phù hợp, nhưng chưa đủ điều kiện để fit vì còn thiếu số, source data hoặc metadata. Đây là trạng thái chủ ý.

`validation_candidate=true` nghĩa là paper có thể dùng để kiểm tra hướng hoặc xu hướng sau khi model được hiệu chuẩn. Validation không nhất thiết cần dùng cùng metric với calibration, nhưng metric phải được định nghĩa và harmonize trước.

Không paper nào trong nhóm này được gắn trạng thái `approved` chỉ bằng việc đọc abstract. Cần reviewer xác nhận:

- genotype và control
- tuổi và giới tính
- nhiệt độ và điều kiện nuôi
- assay và thời lượng
- đơn vị mẫu: ruồi, trial hay experiment
- statistic: mean, median, CI, SD hoặc SEM
- figure/table/source-data reference
- numeric value và uncertainty

## Những điều không được làm

- Không gọi `motor_vigor` là dopamine loss.
- Không gọi climbing defect là chẩn đoán Parkinson.
- Không biến rescue di truyền thành hiệu quả thuốc.
- Không gộp larval crawling với adult walking.
- Không gộp flight với walking speed.
- Không lấy age-dependent decline làm fatigue nếu paper không đo fatigue.
- Không fit asymmetry khi không có left-right data.
- Không điền số từ trí nhớ hoặc từ hình ảnh không chắc chắn.

## Quy trình review cho Pink1

1. Mở bài gốc từ link trong `paper_information.json`.
2. Đối chiếu title/DOI/PMID/journal/year.
3. Đọc methods để xác nhận assay, age, sex, n và control.
4. Đọc figure/table/source data và chép số kèm đơn vị.
5. Cập nhật `candidate_review.csv` và cột mapping tương ứng.
6. Đánh dấu `approve`, `reject` hoặc `edit` trong workspace review.
7. Chỉ record đã approve mới được đưa vào Phenotype Atlas.
8. Sau khi đủ target, thiết kế calibration/holdout split.

## Trạng thái hiện tại

- Có 18 candidate Pink1.
- Một số bài có assay trực tiếp: climbing, flight, crawling, negative geotaxis hoặc trajectory.
- Chưa có numeric target nào được phê duyệt.
- Chưa có disease layer parameter nào được thay đổi dựa trên nhóm này.
- Nhóm Parkin, DJ-1, alpha-synuclein và LRRK2 chưa được bắt đầu trong workflow này.

## Tài liệu nguồn tiêu biểu

- [TRAP1 rescues PINK1 loss-of-function phenotypes](https://pmc.ncbi.nlm.nih.gov/articles/PMC3690968/)
- [Superoxide dismutating molecules rescue PINK1 and parkin loss](https://pmc.ncbi.nlm.nih.gov/articles/PMC5905640/)
- [The STING pathway and Pink1/parkin phenotypes](https://pmc.ncbi.nlm.nih.gov/articles/PMC7021792/)
- [PINK1/Parkin and IP3R-mediated ER calcium release](https://pmc.ncbi.nlm.nih.gov/articles/PMC10457342/)
- [PINK1 trajectory and L-DOPA behavioral analysis](https://www.nature.com/articles/s42003-022-03830-x)
- [Cdk8/CDK19 suppression of Pink1 deficiency](https://pmc.ncbi.nlm.nih.gov/articles/PMC11026413/)

## Kết luận sử dụng

Bộ mapping hiện tại là **bản đồ giả thuyết có nguồn**, không phải ground truth sinh học. Giá trị chính của nó là giúp nhóm biết paper nào có thể cung cấp target nào, mức tin cậy đến đâu và còn thiếu bước kiểm tra nào trước calibration.
