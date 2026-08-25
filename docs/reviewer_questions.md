# Reviewer Questions

> Tài liệu này chỉ liệt kê câu hỏi có thể được reviewer đặt ra. Không có câu trả
> lời, số liệu hoặc kết luận nào được đưa vào.

1. Disease Layer có phải là một biological Parkinson model không?
2. Vì sao nghiên cứu dùng một computational locomotion model?
3. Vì sao chọn motor vigor làm proxy?
4. Vì sao chọn coordination làm proxy?
5. Cơ sở nào để chọn noise, delay và fatigue?
6. Vì sao chưa có dopamine neuron trong mô hình?
7. Vì sao chưa mô phỏng neural connectome?
8. Vì sao chưa mô phỏng dopamine dynamics?
9. Vì sao chưa có alpha-synuclein aggregation?
10. Vì sao chưa có gene expression hoặc cell death?
11. Vì sao chưa có wet-lab validation?
12. Vì sao FlyGym phù hợp với câu hỏi locomotion này?
13. FlyGym version và MuJoCo version được kiểm soát như thế nào?
14. Healthy baseline được định nghĩa và kiểm tra ra sao?
15. Vì sao chọn số seed như trong benchmark matrix?
16. Vì sao chọn số steps và observation duration này?
17. Các rollout có cùng timestep và protocol không?
18. Làm thế nào kiểm tra timestamps và quaternion?
19. Làm thế nào bảo đảm không có NaN/Inf?
20. Vì sao yêu cầu thorax displacement lớn hơn 0?
21. Walking speed có nhiều implementation variant không?
22. Metric nào là primary endpoint và metric nào là secondary endpoint?
23. COM displacement đã được định nghĩa canonical chưa?
24. Pause fraction phụ thuộc threshold và bout duration như thế nào?
25. Left/right symmetry mapping được xác nhận ra sao?
26. Các frames trong một rollout có bị xem nhầm là independent replicates không?
27. Khi nào dùng bootstrap và khi nào dùng permutation test?
28. Khi nào mixed-effects model là hợp lệ với cấu trúc seed/batch?
29. Multiplicity và confidence interval được xử lý như thế nào?
30. Technical parameter sweep được phân biệt với biological calibration target như thế nào?
31. Vì sao literature hiện chưa cung cấp quantitative target đủ dùng?
32. Làm thế nào xử lý metric hoặc channel bị thiếu?
33. Làm thế nào xác định một failed run không bị loại bỏ có chủ đích?
34. Artifact manifest và checksum được kiểm tra độc lập như thế nào?
35. Kết quả computational có thể được gọi là clinical prediction không?
36. Mô hình có thể được dùng để kết luận drug response hoặc therapeutic efficacy không?
37. Holdout calibration được chọn trước hay sau khi xem kết quả?
38. Kết quả có tái lập trên phần cứng và runtime khác không?
39. Các limitation nào còn lại trước khi diễn giải với literature?
40. Kết luận nào được hỗ trợ trực tiếp bởi simulation và kết luận nào chưa được hỗ trợ?

