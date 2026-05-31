# Real Lift2 Example

This example shows a Lift2 real-robot setup for TBot-SA1. The flow is split
across two machines:

- `serve`: loads the checkpoint and answers websocket requests.
- `run`: reads ROS observations and executes returned action chunks.

## Entry Points

- `01_serve_tbot_sa1_real_lift2.sh`: start the TBot-SA1 server.
- `run_real_lift2_inference.sh`: start the robot-side loop.
- `02_inference_lift2.sh`: one-shot launcher for the full stack.
- `test_remote_server.py`: connectivity smoke test.
- `remote_client.py`: lightweight client wrapper for custom loops.

## Runtime

- State and action are 14D.
- Request images are `cam_high`, `cam_left_wrist`, and `cam_right_wrist`.
- The first successful inference waits for manual safety confirmation.
- `DISABLE_3D_TEACHER_FOR_EVAL=true` is the default.
- `STATS_PATH` is optional; if omitted, the server uses `CHECKPOINT_DIR/stats.json`.

## Quick Start

Serve:

```bash
CHECKPOINT_DIR=/path/to/TBot-SA1/checkpoints/060000 \
ACTION_MODE=abs \
INFER_HORIZON=50 \
bash evaluation/Real_Lift2_Example/01_serve_tbot_sa1_real_lift2.sh
```

`CHECKPOINT_DIR` can point to a checkpoint step dir or directly to
`pretrained_model/`. `ACTION_MODE=delta` is also supported when it matches the
checkpoint.

Run:

```bash
WS_URL=ws://127.0.0.1:8000 \
PROMPT="Clear the junk and items off the desktop." \
FRAME_RATE=60 \
IMAGE_HISTORY_INTERVAL=15 \
INFERENCE_MODE=sync \
bash evaluation/Real_Lift2_Example/run_real_lift2_inference.sh
```

Only set `SEND_IMAGE_HEIGHT` and `SEND_IMAGE_WIDTH` if you want a
bandwidth/latency tradeoff.

## Key Env Vars

Serve:

- `CHECKPOINT_DIR`
- `STATS_KEY`
- `STATS_PATH`
- `ACTION_MODE`
- `INFER_HORIZON`
- `NUM_INFERENCE_STEPS`
- `QWEN3_VL_PRETRAINED_PATH`
- `QWEN3_VL_PROCESSOR_PATH`
- `COSMOS_TOKENIZER_PATH_OR_NAME`
- `DA3_MODEL_PATH_OR_NAME`
- `DA3_CODE_ROOT`

Run:

- `WS_URL`
- `PROMPT`
- `FRAME_RATE`
- `IMAGE_HISTORY_INTERVAL`
- `SEND_IMAGE_HEIGHT`
- `SEND_IMAGE_WIDTH`
- `INFERENCE_MODE`

## Smoke Test

```bash
python evaluation/Real_Lift2_Example/test_remote_server.py --ws_url ws://127.0.0.1:8000
python evaluation/Real_Lift2_Example/test_remote_server.py --ws_url ws://127.0.0.1:8000 --smoke_infer
```

## Notes

- If you enable the 3D teacher, make sure the serve env can import
  `depth_anything_3`.
