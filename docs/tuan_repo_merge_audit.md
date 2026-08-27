# Audit merge repository cua Tuan

## Pham vi

Archive duoc review: `E:/drosophila-pd-flygym.zip`.

- Kich thuoc archive: `896672675` bytes.
- SHA-256: `A17AFC24972EBA2C368D3DCA64CDAD23E3D4BB915D10D69608BB7DE89AE04FF4`.
- Archive co root `drosophila-pd-flygym/` va khoang 29 nghin member.
- Phan lon dung luong la `.git`, `.venv`, cache va du lieu thuc nghiem lon.

Day la audit merge co chon loc, khong phai thao tac ghi de toan bo repository.
Archive cu hon commit hien tai cua repository chinh; nhieu file chi khac line
ending, con mot so script phu thuoc source `fly-brain` ben ngoai.

## Da merge

- `src/drosophila_pd/perturbations/brain_driven.py`: bridge tuy chon tu
  `bridge_scales.json` vao action scale, bilateral scale va CPG coupling hien co.
- `src/drosophila_pd/perturbations/__init__.py`: expose hai perturbation bridge.
- `scripts/run_brain_driven_experiment.py`: CLI tuong thich cho paired report,
  delegate vao experiment API hien co.
- `notebooks/colab/30_Brain_Body_GPU_Demo.ipynb`: notebook goi runner brain-body
  that, xac nhan GPU, frame, timestamp, quaternion va bundle.
- `tests/test_brain_driven_perturbation.py`: regression cho scale, bilateral
  preservation, CPG coupling va invalid input.

Duong chay frame-level chinh van la
`scripts/run_brain_body_rollout.py`: BrainEngine -> FlyGym/MuJoCo ->
RolloutRecorder -> rollout export -> analysis/biomarkers -> viewer pose ->
viewer bundle.

## Khong merge vao Git

- `.git/`, `.venv/`, `__pycache__/`, file `.pyc` va cache: khong phai source.
- `data/2025_Connectivity_783.parquet` va cac weights `.pt`: raw/large data,
  can provenance va kenh phat hanh rieng; parquet vuot gioi han file thong
  thuong cua GitHub.
- `results/`, `colab_results_7models/`, MP4 va JSON summary: output da sinh,
  khong co raw rollout day du; khong dung lam ket qua moi.
- `data/bridge_scales/`: cac gia tri co tham chieu source/commit ben ngoai va
  claim literature chua duoc audit trong repository nay. Khong tu dong coi
  chung la calibration target hay biological evidence.
- Cac script batch cu phu thuoc `fly-brain` va private/internal engine state;
  khong chuyen thanh pipeline thu hai. Runner brain-body hien tai la duong
  chay canonical.

## Artifact nhom cung cap

Cac JSON/MP4 trong `E:/VideoDemo` va archive video la derived artifacts. JSON
co the parse va co report paired baseline/perturbed, nhung khong chua
`rollout.json`, `rollout.npz` hay `viewer_pose.json`; MP4 khong the phuc hoi
frame-level state mot cach trung thuc. Vi vay chung khong duoc dong goi lai
thanh rollout moi.

## Runtime that da kiem tra

Tren may hien tai, runner da chay voi CUDA va ghi artifact that:

- brain device: `cuda`;
- brain neurons: `138639`;
- frames trong smoke run: `11` (`10` simulation steps + frame dau);
- quaternion viewer: finite, norm bang `1`;
- timestamp: strictly increasing;
- `brain_body_manifest.json`: hash khop;
- `viewer_bundle.zip`: co `viewer_bundle/index.html` va
  `viewer_bundle/viewer_pose.json`.

Day la xac nhan software/runtime cua computational locomotion pipeline, khong
phai biological Parkinson validation.

## GitHub Pages

`.github/workflows/deploy_pages.yml` deploy `web/` nhu mot static application.
Pose that duoc sinh trong `results/` bi ignore de tranh commit raw artifact.
Do do Pages co the chay viewer shell, nhung khong the tu hien thi mot rollout
that neu khong co `viewer_pose.json` duoc phat hanh kem. Bundle co pose la artifact
deploy doc lap; khong mo bundle bang `file://` neu browser chan fetch JSON.

## Cach chay

Tu repository chinh, voi Python 3.12 va moi truong brain source da co:

```powershell
python scripts/run_brain_body_rollout.py `
  --condition healthy `
  --steps 1000 `
  --seed 0 `
  --device cuda `
  --output results/brain_body/healthy_seed_0
```

Notebook `notebooks/colab/30_Brain_Body_GPU_Demo.ipynb` thuc hien baseline va
computational condition. Neu source brain khong nam o sibling `phase-A-clean`,
dat bien moi truong `FLY_BRAIN_ROOT` tro den source co du
`brain_body_bridge.py`, connectome, completeness table va checkpoint.
