# CAD Files

**Owner: Victor**

Add all chassis CAD files here. Supported formats:

- Fusion 360 (`.f3d`)
- FreeCAD (`.FCStd`)
- STEP (`.step`, `.stp`) — for cross-tool compatibility
- STL (`.stl`) — for 3D printing

## Git LFS

Files over 50MB should use Git Large File Storage:

```bash
git lfs install
git lfs track "*.step"
git lfs track "*.f3d"
git lfs track "*.stl"
git add .gitattributes
git commit -m "chore: add Git LFS tracking for CAD files"
```

## Naming Convention

```
guardian_chassis_v1.step
guardian_arm_mount_v2.f3d
guardian_wheel_bracket.stl
```

## Design Notes

- Chassis must accommodate 4× JGB37-3530 motors with mecanum wheels
- Motor mount spacing determines `wheel_base_length` and `wheel_base_width` in `robot_params.yaml`
- Measure actual dimensions after build and update `30_ros2_ws/src/guardian_bringup/config/robot_params.yaml`
