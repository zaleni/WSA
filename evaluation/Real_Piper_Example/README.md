# Real Piper Example

This example shows a single-arm Piper setup for TBot-SA1. The GPU server loads
the checkpoint and the robot-side client streams observations over a websocket
connection.

## Entry Points

| Server | Robot client |
| --- | --- |
| `01_serve_tbot_sa1_real_piper_sync.sh` | `02_infer_tbot_sa1_real_piper_sync.sh` |

## Shared Runtime

- The client sends `cam_high` and `cam_left_wrist`.
- The action/state vector is 7D.
- `JPEG_ROUNDTRIP=true` matches the reference Piper client.
- `MANUAL_RESET=true` enables Enter-to-reset when `INIT_JOINT_POSITION` is set.

## Common Env

- `CHECKPOINT_DIR`: checkpoint step dir or `pretrained_model` dir.
- `STATS_KEY=real_piper`
- `STATS_PATH`: optional; if unset, the server uses `pretrained_model/stats.json`.
- `ACTION_MODE`: keep this aligned with the checkpoint.
- `INFER_HORIZON`: server-side chunk length.
- `QWEN3_VL_PRETRAINED_PATH`, `QWEN3_VL_PROCESSOR_PATH`,
  `COSMOS_TOKENIZER_PATH_OR_NAME`: TBot-SA1 assets.

## Quick Start

```bash
CHECKPOINT_DIR=/path/to/TBot-SA1/real_piper/checkpoints/last/pretrained_model \
STATS_KEY=real_piper \
ACTION_MODE=abs \
INFER_HORIZON=50 \
bash evaluation/Real_Piper_Example/01_serve_tbot_sa1_real_piper_sync.sh

WS_HOST=<server-ip> \
WS_PORT=8000 \
bash evaluation/Real_Piper_Example/02_infer_tbot_sa1_real_piper_sync.sh
```

## Notes

- `CHECKPOINT_DIR` can point to the checkpoint step dir or directly to
  `pretrained_model/`.
- If `STATS_PATH` is omitted, the server uses the checkpoint's own `stats.json`.
