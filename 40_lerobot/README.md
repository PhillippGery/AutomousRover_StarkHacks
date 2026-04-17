# LeRobot

**Owner: Dipam**

This folder contains LeRobot-specific configs, training datasets, and trained policy checkpoints for GUARDIAN's dual-arm manipulation system.

## Subfolders

| Folder | Contents |
|--------|----------|
| [configs/](configs/) | Policy configuration YAML files |
| [training/](training/) | Training scripts and logs |
| [datasets/](datasets/) | Recorded demonstration datasets |

## Setup

Follow the official LeRobot documentation: https://github.com/huggingface/lerobot

```bash
cd ~/GUARDIAN/30_ros2_ws/src
git clone https://github.com/huggingface/lerobot
cd lerobot
pip install -e ".[feetech]"
```

## Workflow

1. **Collect demonstrations** — run `guardian_arms/scripts/collect_training_data.py` with leader arms to record episodes
2. **Train policy** — use `40_lerobot/configs/guardian_policy_config.yaml` to configure and train ACT or Diffusion Policy
3. **Deploy** — load checkpoint in `arm_manager_node.py` for autonomous execution

## Hardware

- SO-101 leader arms (for teleoperation and demonstration recording)
- SO-101 follower arms mounted on GUARDIAN chassis
