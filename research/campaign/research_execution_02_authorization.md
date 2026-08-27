# Research Execution 02: Conditional Use Authorization

## Muc dich

Tai lieu nay ghi nhan chi dao cho phep chay calibration computational co dieu kien
tren bo target cua Research Execution 02. Day khong phai la chu ky phe duyet khoa hoc
cua research lead va khong thay the viec review tung source.

## Pham vi duoc phep

- Chay calibration engine hien co tren target `7.8 mm/s` cua Riemensperger et al.
  (2011), Figure 2A.
- Danh gia holdout doc lap `2.5 mm/s` cua Pokrzywa et al. (2017), Figure 2A.
- Bao cao sai so, assay mismatch, duration mismatch va transfer assumption.
- Giu tach biet calibration paper va holdout paper theo `paper_id`.

## Pham vi khong duoc phep

- Khong goi computational match la biological validation.
- Khong goi condition duoc chon la Parkinson stage, co che benh, hay ket qua sinh hoc.
- Khong dung ket qua cho diagnosis, clinical prediction, treatment evidence hay drug
  response.
- Khong bien cac gia tri reference-only thanh target calibration.

## Trang thai target

Trang thai trong file target van la `PROPOSED_PENDING_HUMAN_APPROVAL`. Ban ghi nay chi
cho phep su dung computational co dieu kien theo chi dao cua project owner; no khong
doi trang thai review nguon va khong tao ra phe duyet sinh hoc.

| Vai tro | Paper | Metric | Gia tri | Trang thai su dung |
| --- | --- | --- | ---: | --- |
| Calibration | Riemensperger et al. (2011) | `mean_planar_speed_mm_s` | 7.8 mm/s | Conditional use |
| Holdout | Pokrzywa et al. (2017) | `mean_planar_speed_mm_s` | 2.5 mm/s | Independent evaluation only |

## Dieu kien truoc khi cong bo

Research lead can xac nhan:

- DOI/PMCID va source location.
- Gia tri, don vi va statistic type.
- Genotype, age, sex va assay.
- Gia dinh chuyen doi giua assay literature va rollout FlyGym.
- Paper-level split khong leakage.
- Acceptance rule neu muon goi mot ket qua la dat nguong computational.

## Gioi han coverage

Bo target hien chi co mot metric co gia tri so hoc cho calibration va mot holdout cung
metric tu assay khac. Path length, heading, pause, joint, symmetry, orientation va COM
chua co numeric target duoc review trong bo nay. Khong duoc dien giai viec thieu target
la khong co phenotype.

## Nguon

- Riemensperger et al. (2011): https://pmc.ncbi.nlm.nih.gov/articles/PMC3021077/
- Pokrzywa et al. (2017): https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0184117
