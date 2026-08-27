# Computational locomotion condition demo

Tai lieu nay mo ta mot condition de xem truc tiep tren viewer bang Disease Layer
hien co. Day la mot **computational locomotion condition**, khong phai biological
Parkinson model, khong phai clinical prediction, diagnosis, drug response hay
therapeutic validation.

## Vi sao con ruoi bot "may moc"

Healthy controller cua project la official FlyGym CPG tripod. No tao ra nhiem
vu dieu khien co chu ky, nen healthy rollout co the deu va co tinh co hoc cao.
Viewer chi hien thi cac frame that; no khong tu them AI hay hanh vi.

Condition demo lam bien doi action/controller o lop Disease Layer bang cac
proxy da co:

- `motor_vigor`: giam bien do lenh khop;
- `coordination`: giam coupling cua CPG;
- `initiation_delay_steps`: cham bat dau van dong;
- `action_latency_steps`: dung lenh khop tre hon;
- `motor_noise_std`: them noise nho, co seed;
- `fatigue_rate`: giam dan bien do theo thoi gian;
- `freezing_probability` va `freezing_duration_steps`: tao pause episode co
  xac suat va thoi luong cau hinh duoc.

Day la cac control-level proxies. Cac gia tri trong file demo la diem de quan
sat va kiem tra pipeline, khong phai gia tri sinh hoc da duoc fit tu literature.

## Chay simulation va tao viewer

Tu repository root, trong Python 3.12 environment da pass runtime check:

```powershell
python scripts/run_calibration_conditions.py `
  --baseline-config configs/experiments/healthy_baseline.yaml `
  --conditions configs/parkinson/computational_pd_like_demo.yaml `
  --output results/computational_pd_like_demo `
  --export-viewer
```

Lenh nay chay healthy baseline va condition demo bang FlyGym that. Khong co
runtime thi lenh that bai va khong tao ket qua gia.

Artifact nam tai:

```text
results/computational_pd_like_demo/
  summary.json
  healthy_baseline.json
  computational_pd_like_demo.json
  artifacts/
    healthy_baseline/
      rollout.json
      rollout.npz
      viewer_pose.json
      viewer_bundle.zip
    computational_pd_like_demo/
      rollout.json
      rollout.npz
      viewer_pose.json
      viewer_bundle.zip
```

Mo bundle bang cach giai nen `viewer_bundle.zip`, sau do mo:

```text
viewer_bundle/index.html
```

Hoac chay viewer server voi pose cua condition:

```powershell
python scripts/run_viewer.py `
  --pose results/computational_pd_like_demo/artifacts/computational_pd_like_demo/viewer_pose.json
```

Viewer chi phat lai rollout da ghi. Play/Pause/Seek, mesh FlyGym that va
trajectory la presentation cua du lieu simulation; chung khong phai phan tich
sinh hoc.

## Cach doc ket qua

So sanh `healthy_baseline.json` voi
`computational_pd_like_demo.json`, truoc het kiem tra:

- `overall_pass` va cac checks;
- `derived_locomotion_metrics`;
- `perturbation.parameters`;
- `action_transformation_summary`;
- `rollout_artifacts.frame_count`;
- validation cua `viewer_pose.json`.

Khong goi condition nay la ket qua Parkinson. De co ket luan khoa hoc, nhom
can co target literature da duyet, calibration co provenance, holdout
validation va nhieu seed theo protocol cua project.

## Gioi han hien tai

`postural_instability` van duoc danh dau unsupported vi FlyGym
`LocomotionAction` hien tai chi expose joint angles va adhesion, khong expose
orientation/body-stabilization command. Khong nen ep proxy nay vao action khi
chua co API phu hop.
