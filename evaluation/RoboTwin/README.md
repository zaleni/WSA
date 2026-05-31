# RoboTwin Evaluation

This document provides instructions for reproducing our experimental results
with [RoboTwin2.0](https://github.com/RoboTwin-Platform/RoboTwin).

The main entry point is `eval_randomized_50.sh`, which runs TBot-SA1 on the
RoboTwin randomized 50-task benchmark. By default it loads the released
`zaleni/TBot-SA1-RoboTwin` checkpoint; you can override the checkpoint, task
range, episode count, and GPU allocation with environment variables.

## Introduction

- `eval_randomized_50.sh`: maintained TBot-SA1 randomized 50-task evaluation
  wrapper. It defaults to `PRETRAINED_CKPT=zaleni/TBot-SA1-RoboTwin`.
- `inference.py`: shared RoboTwin evaluator called by the shell wrapper.
- `image_tools.py`: image processing helpers used by the evaluator.

## Requirements

You can follow the official RoboTwin installation guide for the complete
simulator setup:
[robotwin-platform.github.io/doc/usage/robotwin-install.html](https://robotwin-platform.github.io/doc/usage/robotwin-install.html).

This repository expects the RoboTwin codebase to live under
`third_party/RoboTwin`. If you cloned TBot-SA1 without submodules, initialize the
submodule first:

```bash
git submodule update --init --recursive third_party/RoboTwin
```

If you install RoboTwin manually instead of using submodules, clone it into the
same path:

```bash
git clone https://github.com/RoboTwin-Platform/RoboTwin.git third_party/RoboTwin
```

### Environment Set-up

After the main TBot-SA1 environment is ready, keep using the same environment
and add the RoboTwin simulator dependencies. This follows the RoboTwin 2.0 setup
used by
[LingBot-VA](https://github.com/Robbyant/lingbot-va#evaluation-on-robotwin-20),
but keeps TBot-SA1's PyTorch, Transformers, and Hugging Face Hub versions
intact.

```bash
conda activate tbot_sa1

sudo apt update
sudo apt install -y libvulkan1 mesa-vulkan-drivers vulkan-tools
vulkaninfo
```

Before running RoboTwin's installer, replace RoboTwin's default requirements
with the TBot-SA1-compatible extra requirements in this directory. The installer
will run `pip install -r script/requirements.txt`, so do not install the same
file separately unless you are skipping `_install.sh`.

```bash
cp evaluation/RoboTwin/requirements.txt third_party/RoboTwin/script/requirements.txt
```


Then install RoboTwin's remaining native/simulator dependencies and download the
simulation assets:

```bash
cd third_party/RoboTwin
bash script/_install.sh
bash script/_download_assets.sh
cd ../..
```


For TBot-SA1, install `transformers==4.57.1` and patch the installed Qwen3-VL
code with `src/lerobot/policies/TBot_SA1/transformers_replace/models`.


## Quick Start

```bash
PRETRAINED_CKPT=zaleni/TBot-SA1-RoboTwin \
QWEN3_VL_PRETRAINED_PATH=Qwen/Qwen3-VL-2B-Instruct \
QWEN3_VL_PROCESSOR_PATH=Qwen/Qwen3-VL-2B-Instruct \
COSMOS_TOKENIZER_PATH_OR_NAME=nvidia/Cosmos-Tokenizer-CI8x8 \
DISABLE_DA3_TEACHER_FOR_EVAL=true \
ACTION_MODE=delta \
GPU_IDS=0,1 \
MAX_JOBS_PER_GPU=2 \
bash evaluation/RoboTwin/eval_randomized_50.sh
```

## Common Options

- `PRETRAINED_CKPT`: checkpoint directory or Hugging Face model id. Defaults to
  `zaleni/TBot-SA1-RoboTwin`.
- `GPU_IDS`: comma-separated GPUs used by the scheduler, for example `0,1`.
- `MAX_JOBS_PER_GPU`: maximum parallel RoboTwin tasks per GPU. Lower this if
  memory is tight.
- `TASK_CONFIG`: RoboTwin task config setting `demo_clean` or `demo_randomized`. The default is set to
  `demo_randomized`.
- `START_TASK_IDX` and `TASK_COUNT`: evaluate a slice of the 50
  tasks, useful for debugging or resuming partial runs.
- `TEST_NUM`: number of episodes per task. Defaults to `100`.
- `ACTION_MODE`: action representation expected by the checkpoint. The released
  RoboTwin checkpoint uses `delta`.
- `INFER_HORIZON` and `ACTION_HORIZON_SIZE`: policy rollout horizon settings.
  Keep the defaults unless you are matching a custom checkpoint.
- `DISABLE_DA3_TEACHER_FOR_EVAL`: keep this `true` for standard action
  evaluation without loading the 3D teacher.
- `QWEN3_VL_PRETRAINED_PATH`, `QWEN3_VL_PROCESSOR_PATH`, and
  `COSMOS_TOKENIZER_PATH_OR_NAME`: override these only when using local copies
  of the backbone, processor, or tokenizer.

## Outputs

Each run writes per-task logs under `evaluation/RoboTwin/output*/tasks/task_##/` with:

- `summary.json`
- `summary.txt`
- `job_status.tsv`

## Notes

- `ACTION_MODE` should match the checkpoint/training setup, `abs` or `delta`.
- `STATS_KEY` is usually `aloha`.
