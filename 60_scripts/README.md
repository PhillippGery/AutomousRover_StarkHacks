# Scripts

Convenience shell scripts for setup, building, and running GUARDIAN.

| Script | Purpose |
|--------|---------|
| `setup_amd_minipc.sh` | One-shot install of all system dependencies on Ubuntu 22.04 |
| `build_workspace.sh` | Source ROS2, install deps, build workspace |
| `run_guardian.sh` | Interactive launch menu |

## Usage

```bash
# First-time setup (run once after cloning)
bash 60_scripts/setup_amd_minipc.sh

# Build workspace
bash 60_scripts/build_workspace.sh

# Launch
bash 60_scripts/run_guardian.sh
```
