# RoboTwin Evaluation

This directory evaluates TBot-SA1 and comparison methods on RoboTwin. The shared
evaluator is `evaluation/RoboTwin/inference.py`; the shell scripts set
checkpoints, stats, and job scheduling knobs.

## Entry Points

- `eval_randomized_50.sh`: maintained TBot-SA1 randomized eval wrapper.
- `eval_tbot_sa1_3B.sh`: TBot-SA1 eval wrapper.
- `eval_qwenaction_50.sh`: QwenAction comparison eval wrapper.
- `eval.sh`: lower-level single-run launcher.
- `inference.py`: shared evaluator.

## Requirements

- Linux with an NVIDIA GPU
- Python 3.10
- CUDA 12.8
- PyTorch 2.7.1
- `third_party/RoboTwin` checked out and its assets downloaded
- Vulkan runtime installed

For TBot-SA1, install `transformers==4.57.1` and patch the installed Qwen3-VL
code with `src/lerobot/policies/TBot_SA1/transformers_replace/models`.

## Quick Start

```bash
PRETRAINED_CKPT=/path/to/TBot-SA1/pretrained_model \
QWEN3_VL_PRETRAINED_PATH=/path/to/Qwen3-VL-2B-Instruct \
QWEN3_VL_PROCESSOR_PATH=/path/to/Qwen3-VL-2B-Instruct \
COSMOS_TOKENIZER_PATH_OR_NAME=/path/to/Cosmos-Tokenizer-CI8x8 \
DISABLE_DA3_TEACHER_FOR_EVAL=true \
GPU_IDS=0,1 \
MAX_JOBS_PER_GPU=2 \
bash evaluation/RoboTwin/eval_randomized_50.sh
```

## Key Env Vars

- `PRETRAINED_CKPT`
- `GPU_IDS`
- `MAX_JOBS_PER_GPU`
- `TASK_CONFIG`
- `START_TASK_IDX`
- `TASK_COUNT`
- `TEST_NUM`
- `ACTION_MODE`
- `STATS_KEY`
- `INFER_HORIZON`
- `BINARIZE_GRIPPER`
- `SKIP_GET_OBS_WITHIN_REPLAN`
- `DECODE_IMAGE_FLAG`
- `DISABLE_DA3_TEACHER_FOR_EVAL`
- `QWEN3_VL_PRETRAINED_PATH`
- `QWEN3_VL_PROCESSOR_PATH`
- `COSMOS_TOKENIZER_PATH_OR_NAME`
- `DA3_MODEL_PATH_OR_NAME`
- `DA3_CODE_ROOT`

## Outputs

Each run writes per-task logs under `evaluation/RoboTwin/output*/tasks/task_##/`,
plus:

- `summary.json`
- `summary.txt`
- `job_status.tsv`

## Notes

- `ACTION_MODE` should match the checkpoint/training setup.
- `STATS_KEY` is usually `aloha`.
- If you need the CVPR 2026 11-task subset, use task ids
  `[2, 3, 9, 10, 12, 15, 17, 25, 28, 30, 44]`.
