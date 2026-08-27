# Research Execution 02: Target Coverage

## Ket qua

Bo du lieu hien tai chi co mot metric co target so hoc cho calibration:
`mean_planar_speed_mm_s` voi `7.8 mm/s` tu Riemensperger et al. (2011). Holdout doc
lap cung metric co gia tri `2.5 mm/s` tu Pokrzywa et al. (2017). Hai gia tri nay duoc
tach theo paper-level split va deu duoc danh dau `CONDITIONAL` vi assay, age/context va
duration khong tuong duong hoan toan voi rollout FlyGym.

## Cac metric chua co target tuong thich

`planar_path_length_mm` chi co gia tri reference-only trong register. Cac metric
`heading_yaw_change_rad`, `trajectory_efficiency`, `pause_fraction`, `joint_velocity`,
`symmetry_index`, `orientation_stability` va `com_displacement` chua co numeric target
duoc review trong bo split nay.

`UNAVAILABLE_TARGET` co nghia la chua du du lieu de fit hoac validate metric do; no
khong phai ket luan rang simulation khong co hien tuong tuong ung.

## He qua phuong phap

- Calibration hien tai la bai toan mot target, mot metric; khong nen goi la multi-metric
  calibration.
- Holdout duoc dung de mo ta sai so tren paper khac, khong co acceptance threshold va
  khong phai biological validation.
- Khong duoc tu suy ra target cho cac metric con lai tu cac gia tri speed, distance,
  phan tram effect hay stop duration.
- Muon mo rong calibration can paper-level numeric extraction, unit/statistic review,
  assay compatibility review va approval rieng cho tung target.

## Kiem tra da hoan tat

- [x] Calibration va holdout khong trung `paper_id`.
- [x] Don vi cua metric da chon la `mm/s`.
- [x] Source location va URL duoc luu trong target records.
- [x] Assay mismatch duoc ghi ro.
- [x] Khong tao so lieu moi cho metric chua co target.
