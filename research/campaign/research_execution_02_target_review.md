# Research Execution 02: Numeric Target Review

## Muc tieu

Tai lieu nay ghi lai cach hai numeric literature target duoc dua vao mot split
doc lap de kiem tra calibration cua metric `mean_planar_speed_mm_s`. Day la
calibration tinh toan co dieu kien, khong phai biological validation va khong
phai ket luan ve Parkinson.

## Nguon va gia tri da kiem tra

1. **Riemensperger et al. (2011), PNAS, PMCID PMC3021077**
   - Figure 2A bao cao median walking speed 7.8 mm/s cho nhom thieu dopamine
     than kinh, 10.8 mm/s cho nhom rescued-control va 15 mm/s cho wild type.
   - Gia tri `7.8 mm/s` duoc dat vao calibration split.
   - Cung bai bao bao cao covered distance 193, 425 va 474 cm trong 15 phut;
     cac gia tri nay giu o reference register vi duration va dinh nghia path
     khong tuong duong rollout hien tai.

2. **Pokrzywa et al. (2017), PLOS ONE, DOI 10.1371/journal.pone.0184117**
   - Figure 2A va Results mo ta mean velocity cua ruoi bieu hien
     alpha-synuclein giam tu 5.6 xuong 2.5 mm/s trong ba tuan dau; control
     giam tu 6 xuong 5 mm/s.
   - Gia tri `2.5 mm/s` duoc giu lam holdout theo paper-level split.
   - Nguon dung FlyTracker, ghi 10 giay o 30 frames/s theo tuan; endpoint nay
     khong trung hoan toan voi flat-ground FlyGym rollout 0.5 giay.

## Trang thai review

- Machine-readable target database:
  `research_execution_02_numeric_targets.json`
- CSV review view:
  `research_execution_02_numeric_targets.csv`
- Paper-level split:
  `research_execution_02_split_manifest.json`
- Trang thai hien tai: `PROPOSED_PENDING_HUMAN_APPROVAL`.
- Khong duoc goi la `approved` cho den khi research lead xac nhan source
  location, unit, assay, age, genotype va transfer assumption.

## Quy tac khong leakage

- Calibration va holdout khong dung chung `paper_id`.
- Khong dung control value lam disease target.
- Khong chuyen doi gia tri 15-minute covered distance sang path length cua
  rollout ngan.
- Khong dua stop duration, threat response, climbing hay relative percent
  effect vao engine vi simulation metric hien tai khong tuong thich.

## Cach phe duyet thu cong

Nguoi review can ky/xac nhan tung dong trong CSV:

- [ ] DOI/PMCID va source URL da kiem tra.
- [ ] Gia tri nam dung trong bai/figure da ghi.
- [ ] Don vi va statistic type (median/mean/time-course) da ghi.
- [ ] Genotype, age, sex va assay da ghi.
- [ ] Da chap nhan hay tu choi transfer sang metric FlyGym.
- [ ] Da xac nhan split calibration/holdout khong leakage.

## Ket luan pham vi

Calibration report chi duoc dien giai la muc do khop cua cac cau hinh action-level
voi numeric observations duoc cung cap. No khong chung minh mo hinh sinh hoc
Parkinson, khong phai chan doan, du doan lam sang, hay danh gia dap ung thuoc.
