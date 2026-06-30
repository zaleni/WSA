# LIBERO Evaluation

This document provides instructions for evaluating WSA on LIBERO with a
split two-environment setup:

- `wsa_base` environment: serves policy inference over a local websocket.
- `libero` environment: runs LIBERO benchmark rollouts.

The two processes usually run on the same machine and communicate through a
local websocket such as `ws://127.0.0.1:8000`.

## Relevant files

- `01_serve_wsa_base_libero.sh`: start the WSA policy server.
- `eval.sh`: run LIBERO benchmark rollouts.
- `inference.py`: main LIBERO evaluation logic.
- `model_server.py`: policy server entrypoint.
- `websocket_server.py`, `websocket_client.py`, and `libero_remote_client.py`:
  websocket transport helpers.
- `msgpack_numpy.py`: msgpack NumPy codec helper.

## Install

Recommended layout: keep LIBERO at `third_party/LIBERO`.

You need dependencies on both sides:

- `libero` env: official LIBERO stack, plus this repo's evaluator extras.
- `wsa_base` env: WSA serving stack, plus `tyro`, `matplotlib`,
  `mediapy`, `websockets`, and `msgpack`.

Because LIBERO evaluation uses a separate environment, it is fine to follow the
official LIBERO install flow:

```bash
conda activate libero
git submodule update --init --recursive third_party/LIBERO
cd third_party/LIBERO
pip install -r requirements.txt
pip install tyro imageio websockets msgpack
pip install -e .
cd ../..
```

Or use the helper script:

```bash
conda activate libero
bash evaluation/Libero/install_libero.sh
```

If the `wsa_base` environment does not already have the extra serve-side
dependencies, install:

```bash
conda activate wsa_base
pip install tyro matplotlib mediapy websockets msgpack
```

Quick checks:

```bash
python -c "from libero.libero import benchmark; print('LIBERO OK')"
python -c "from libero.libero.envs import OffScreenRenderEnv; import robosuite, bddl; print('LIBERO eval deps OK')"
python -c "import websockets.sync.client, msgpack; print('Split websocket deps OK')"
```

For headless machines, you may also need:

```bash
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
```

## Dataset Prep

This section is only needed for LIBERO training data. Evaluation-only benchmark
runs do not need a LeRobot dataset.

Download the four LIBERO LeRobot datasets:

```bash
python -m pip install -U "huggingface-hub[cli]>=0.34.2,<0.36.0"

export LIBERO_DATA_ROOT=/path/to/LEROBOT_LIBERO_DATA
mkdir -p "$LIBERO_DATA_ROOT"

for REPO in \
  IPEC-COMMUNITY/libero_spatial_no_noops_1.0.0_lerobot \
  IPEC-COMMUNITY/libero_object_no_noops_1.0.0_lerobot \
  IPEC-COMMUNITY/libero_goal_no_noops_1.0.0_lerobot \
  IPEC-COMMUNITY/libero_10_no_noops_1.0.0_lerobot
do
  hf download "$REPO" --repo-type dataset --local-dir "$LIBERO_DATA_ROOT/${REPO##*/}"
done
```

The downloaded folders are usually LeRobot v2.1 datasets. WSA training
expects LeRobot v3.0 folders under `LIBERO_ROOT`, for example
`libero_goal_no_noops_1.0.0_lerobot_v30`.

Convert them from the repo root:

```bash
for NAME in \
  libero_spatial_no_noops_1.0.0_lerobot \
  libero_object_no_noops_1.0.0_lerobot \
  libero_goal_no_noops_1.0.0_lerobot \
  libero_10_no_noops_1.0.0_lerobot
do
  PYTHONPATH=./src python -m lerobot.datasets.v30.convert_dataset_v21_to_v30 \
    --repo-id="$NAME" \
    --root="$LIBERO_DATA_ROOT" \
    --push-to-hub=false
done
```

This keeps the original v2.1 folders and writes sibling v3.0 folders with the
`_v30` suffix. Then point `LIBERO_ROOT` to the parent directory that contains
those `libero_*_lerobot_v30` folders.

Compute the merged normalization stats used by LIBERO finetuning:

```bash
export LIBERO_STATS_ROOT=/path/to/norm_stats/libero_all_chunk10
export LIBERO_REPO_ID_FILE=/tmp/libero_v30_datasets.txt

printf '%s\n' \
  "$LIBERO_DATA_ROOT/libero_spatial_no_noops_1.0.0_lerobot_v30" \
  "$LIBERO_DATA_ROOT/libero_object_no_noops_1.0.0_lerobot_v30" \
  "$LIBERO_DATA_ROOT/libero_goal_no_noops_1.0.0_lerobot_v30" \
  "$LIBERO_DATA_ROOT/libero_10_no_noops_1.0.0_lerobot_v30" \
  > "$LIBERO_REPO_ID_FILE"

PYTHONPATH=./src python tools/compute_norm_stats_multi.py \
  --repo_id_file "$LIBERO_REPO_ID_FILE" \
  --action_mode abs \
  --chunk_size 10 \
  --num_workers 8 \
  --output_path "$LIBERO_STATS_ROOT/franka/abs/stats.json"
```

During training, set `DATASET_EXTERNAL_STATS_PATH` to that file, or set
`DATASET_EXTERNAL_STATS_ROOT=$LIBERO_STATS_ROOT`. If you train with a different
action mode or chunk size, keep `--action_mode` and `--chunk_size` aligned with
the training launcher.

## Run

1. Start the policy server in the `wsa_base` environment:

```bash
conda activate wsa_base

PORT=8000 \
CHECKPOINT_DIR=/path/to/checkpoints/last/pretrained_model \
QWEN3_VL_PRETRAINED_PATH=Qwen/Qwen3-VL-2B-Instruct \
COSMOS_TOKENIZER_PATH_OR_NAME=nvidia/Cosmos-Tokenizer-CI8x8 \
STATS_KEY=franka \
ACTION_MODE=abs \
INFER_HORIZON=10 \
bash evaluation/Libero/01_serve_wsa_base_libero.sh
```

2. Start the LIBERO benchmark in the `libero` environment:

```bash
conda activate libero

WS_URL=ws://127.0.0.1:8000 \
TASK_SUITE_NAME=libero_goal \
INFER_HORIZON=10 \
VIDEO_ROOT=$PWD/evaluation/Libero/output \
bash evaluation/Libero/eval.sh
```

3. Evaluate a single task:

```bash
conda activate libero

WS_URL=ws://127.0.0.1:8000 \
TASK_SUITE_NAME=libero_goal \
TASK_ID=0 \
INFER_HORIZON=10 \
bash evaluation/Libero/eval.sh
```

`INFER_HORIZON` note:

- Serve-side `INFER_HORIZON` should usually follow the checkpoint training
  setup, for example `10`.
- Eval-side `INFER_HORIZON` controls how many steps the evaluator executes from
  each returned chunk.
- For shorter replanning during evaluation, keep the serve side at `10` and
  reduce only the eval side, for example `5`.

## Common Options

Serve side:

- `CHECKPOINT_DIR`: checkpoint step directory or `pretrained_model/` directory.
- `HOST` and `PORT`: server bind address. Defaults to `0.0.0.0:8000`.
- `STATS_KEY`: stats entry loaded from the checkpoint. LIBERO uses `franka`.
- `STATS_PATH`: optional explicit `stats.json`; otherwise the server uses the
  checkpoint stats.
- `ACTION_MODE`: action representation expected by the checkpoint, usually
  `abs` for LIBERO.
- `INFER_HORIZON`: action chunk length returned by the server.
- `QWEN3_VL_PRETRAINED_PATH`, `QWEN3_VL_PROCESSOR_PATH`, and
  `COSMOS_TOKENIZER_PATH_OR_NAME`: override these only when using local copies
  of the backbone, processor, or tokenizer.

Eval side:

- `WS_URL`: websocket server address, usually `ws://127.0.0.1:8000`.
- `TASK_SUITE_NAME`: one of `libero_spatial`, `libero_object`, `libero_goal`,
  `libero_10`, or `libero_90`.
- `TASK_ID`: optional single-task index. Leave unset to evaluate the full suite.
- `NUM_TRIALS_PER_TASK`: number of initial states per task. Defaults to `50`.
- `SEED`: evaluation seed. Defaults to `7`.
- `INFER_HORIZON`: optional number of actions executed per returned chunk.
- `VIDEO_ROOT`: outer output root; final path becomes
  `<VIDEO_ROOT>/<TASK_SUITE_NAME>`.
- `VIDEO_DIR`: exact output directory override.
- `PRETRAINED_CKPT`: local single-process evaluation checkpoint. Use this
  instead of `WS_URL` only when not using split websocket serving.

## Outputs

Default output path:

```text
evaluation/Libero/output/<task_suite_name>/
```

If you only want to switch the outer folder, for example from `output` to
`output_0420`, use `VIDEO_ROOT`:

```bash
conda activate libero

WS_URL=ws://127.0.0.1:8000 \
TASK_SUITE_NAME=libero_goal \
INFER_HORIZON=10 \
VIDEO_ROOT=$PWD/evaluation/Libero/output_0420 \
bash evaluation/Libero/eval.sh
```

This writes to:

```text
evaluation/Libero/output_0420/libero_goal/
```

Each task directory contains rollout videos and a task-level `summary.json`.
The suite output directory also contains an overall `summary.json`.
