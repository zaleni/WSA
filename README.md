<h1 align="center">TBot-SA1: a 3D-centric World-Spatial-Action Model
for Generalizable Robot Control</h1>

<p align="center">
  <img src="assets/logo.png" alt="TBot-SA1" width="400">
</p>

<p align="center">
  a <strong>World-Spatial-Action</strong> embodied
  foundation model that unifies instruction-aligned 2D visual planning,
  action-conditioned 3D world modeling, and 3D-aware action generation.
</p>

<p align="center">
  <a href="https://zaleni.github.io/TBot-SA1/"><img src="https://img.shields.io/badge/Project%20Page-Website-2EA44F?logo=googlechrome&logoColor=ffffff" alt="Project page"></a>
  <a href="https://github.com/zaleni/TBot-SA1"><img src="https://img.shields.io/badge/Repository-GitHub-181717?logo=github" alt="GitHub repository"></a>
  <a href="https://zaleni.github.io/TBot-SA1/assets/paper/manuscript.pdf"><img src="https://img.shields.io/badge/Paper-PDF-B31B1B?logo=adobeacrobatreader&logoColor=ffffff" alt="Paper PDF"></a>
  <a href="https://huggingface.co/collections/zaleni/tbot-sa1"><img src="https://img.shields.io/badge/Models-HuggingFace-FFD21E?logo=huggingface&logoColor=000000" alt="Hugging Face models"></a>
  <a href="https://robochallenge.ai/competition/cvpr"><img src="https://img.shields.io/badge/%F0%9F%8F%86%20Leaderboard-RoboChallenge-C99A00" alt="RoboChallenge leaderboard"></a>
</p>

<br>

<p align="center">
  <img src="assets/motivation_01.png" alt="TBot-SA1 overview" width="95%">
</p>

<a id="news"></a>

## 🗞️ News

- [2026-05-18]: 🏆 Our fully open-source WSA model **TBot-SA1 ranked 4th worldwide on the [RoboChallenge CVPR 2026 leaderboard](https://robochallenge.ai/competition/cvpr).** (Team: MagicBot)
- [2026-05-31]: 🎉 Release of TBot-SA1 training, evaluation, and inference code.
- [2026-05-31]: 🤗 Released the WSA paper and the TBot-SA1 Hugging Face
  model collection with Base, RoboTwin, and LIBERO models.

<a id="todo-list"></a>

## TODO List

- [x] Provide RoboTwin, LIBERO, and real world robot example inference workflows.
- [x] Release TBot-SA1 policy code and finetuning scripts.
- [x] Release TBot-SA1 pretraining scripts.
- [ ] Release paper on arxiv and citation.
- [ ] Release results and models on more benchmarks.
- [ ] **[Coming soon] Release TBot-SA1-6B model code, a 6B type of WSA model using Wan2.2 video model as backbone.**
- [ ] **Release TBot-SA1-6B model weights and results.**

## Table of Contents
- [Overview](#overview)
- [Repository Layout](#repository-layout)
- [Installation](#installation)
- [Model Zoo](#model-zoo)
- [Inference](#inference)
- [Training](#training)
  - [RoboTwin Finetuning](#robotwin-finetuning)
  - [Finetuning example](#finetuning-example)
  - [Multi-Dataset Pretraining](#multi-dataset-pretraining)
- [Acknowledgments](#acknowledgments)
- [Citation](#citation)

## Overview

<p align="center">
  <img src="assets/framework_01.png" alt="TBot-SA1 framework" width="95%">
</p>

TBot-SA1 is a **World-Spatial-Action (WSA)** embodied foundation model for
generalizable robot control. It learns a shared 2D-3D latent space that connects
instruction-aligned **visual planning**, action-conditioned **3D world prediction**,
and 3D-aware **action generation**.

### 🌟 Highlights:

- **Unified WSA Modeling:** WSA modeling unifies semantic understanding, 3D world modeling, and physical
  execution.
- **Bidirectional 3D Causality:** Bidirectional 3D causality learns both action-conditioned scene dynamics and
  3D inverse dynamics.
- **Mixture-of-Transformers:** Mixture-of-Transformers coordinates 2D planning, 3D prediction, and 3D action
  generation with shared dependency rules.
- **Data-Efficient Pretraining:** Data-efficient pretraining on 6,000 demonstration hours yields strong
  simulation and real-world manipulation performance.
- **Superior Performance:** State-of-the-art results across simulation
  and real-world robot manipulation tasks, achieved by our open-source model.

---
🤖 Result on RoboTwin 2.0 randomized setting, averaged over 50 simulated aloha manipulation tasks:
| Metric | π0 | π0.5 | ABot-M0 | Motus | InternVLA-A1 | LingBot-VA | Fast-WAM | **TBot-SA1** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Avg. Success (Hard) | 58.40% | 76.76% | 85.08% | 87.02% | 89.64% | 91.50% | 91.78% | **92.70%** |

## Repository Layout

```text
assets/                  README figures and paper assets
configs/                 data sampling and weight-rule configs
evaluation/
  RoboTwin/              RoboTwin evaluation entrypoints
  Libero/                LIBERO evaluation and websocket serving helpers
  Real_Piper_Example/    Piper real-robot serving/client example
  Real_Lift2_Example/    Lift2 real-robot serving/client example
launch/
  tbot_sa1_*.sh          TBot-SA1 pretraining and finetuning scripts
  supported_methods/     RoboTwin finetuning scripts for comparison methods
src/lerobot/             LeRobot-based training, dataset, and policy code
third_party/             Git submodules for external projects
tools/                   support scripts used by training workflows
```

## Installation

The main development environment is tested with Python 3.10, CUDA 12.8, and
PyTorch 2.7.1.

```bash
git clone --recurse-submodules https://github.com/zaleni/TBot-SA1.git
cd TBot-SA1
git submodule update --init --recursive

conda create -y -n tbot_sa1 python=3.10
conda activate tbot_sa1
pip install --upgrade pip

conda install -c conda-forge ffmpeg=7.1.1 svt-av1 -y

pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
  --index-url https://download.pytorch.org/whl/cu128

pip install torchcodec numpy scipy transformers==4.57.1 mediapy loguru pytest omegaconf h5py
pip install -e .
```

For real-robot serving and websocket evaluation:

```bash
pip install tyro matplotlib mediapy websockets msgpack
```

TBot-SA1 uses a patched Qwen3-VL implementation for cached inference. After
installing `transformers==4.57.1`, copy the replacement model files into the
installed package:

```bash
TRANSFORMERS_DIR=${CONDA_PREFIX}/lib/python3.10/site-packages/transformers/
cp -r src/lerobot/policies/TBot_SA1/transformers_replace/models ${TRANSFORMERS_DIR}
```

## Model Zoo

| Name | Type | Usage |
| --- | --- | --- |
| [TBot-SA1-Base](https://huggingface.co/zaleni/TBot-SA1-Base) | Pretrained policy | TBot-SA1 pretrained model for downstream finetuning |
| [TBot-SA1-RoboTwin](https://huggingface.co/zaleni/TBot-SA1-RoboTwin) | RoboTwin finetuned model | Fine-tuned from TBot-SA1-Base for RoboTwin evaluation and inference |
| [TBot-SA1-LIBERO](https://huggingface.co/zaleni/TBot-SA1-LIBERO) | LIBERO finetuned model | Fine-tuned from TBot-SA1-Base for LIBERO evaluation and inference |

All released models are available in the
[TBot-SA1 Hugging Face collection](https://huggingface.co/collections/zaleni/tbot-sa1).

For action evaluation with the released model, use
`DISABLE_DA3_TEACHER_FOR_EVAL=true`.

## Inference

- RoboTwin: [evaluation/RoboTwin/README.md](evaluation/RoboTwin/README.md)
- Real Piper example:
  [evaluation/Real_Piper_Example/README.md](evaluation/Real_Piper_Example/README.md)
- Real Lift2 example:
  [evaluation/Real_Lift2_Example/README.md](evaluation/Real_Lift2_Example/README.md)

The real-robot examples split inference into a GPU policy server and a
robot-side client. They are intended as reference integrations that you can
adapt to your own hardware.

## Training

All TBot-SA1 training scripts live directly under `launch/`.
For finetuning, initialize from the released base pretrained model with
`POLICY_INIT_PATH=zaleni/TBot-SA1-Base`.


### RoboTwin Finetuning

`launch/tbot_sa1_finetune_robotwin.sh` discovers all LeRobot-v3 datasets under
`ROBOTWIN_ROOT` and trains over them as a multi-dataset run.

Download the RoboTwin LeRobot-v3.0 dataset from Hugging Face and point
`ROBOTWIN_ROOT` to the local download directory:

```bash
hf download hxma/RoboTwin-LeRobot-v3.0 \
  --repo-type dataset \
  --local-dir /path/to/robotwin_lerobot_v3.0
```

Compute external normalization statistics before training. The output path below
matches the `DATASET_EXTERNAL_STATS_ROOT=/path/to/norm_stats` layout used by the
training script:

```bash
ROBOTWIN_ROOT=/path/to/robotwin_lerobot_v3.0

find -L "${ROBOTWIN_ROOT}" -path "*/meta/info.json" -print \
  | while read -r info; do dirname "$(dirname "$info")"; done \
  | sort -u > robotwin_repo_ids.txt

python tools/compute_norm_stats_multi.py \
  --repo_id_file robotwin_repo_ids.txt \
  --action_mode delta \
  --chunk_size 50 \
  --num_workers 8 \
  --output_path /path/to/norm_stats/aloha/delta/stats.json
```

If you want to train with `ACTION_TYPE=abs`, compute stats with `--action_mode abs` and write to
`/path/to/norm_stats/aloha/abs/stats.json` instead.

```bash
POLICY_INIT_PATH=zaleni/TBot-SA1-Base \
ROBOTWIN_ROOT=/path/to/robotwin_lerobot_v3.0 \
ACTION_TYPE=delta \
USE_EXTERNAL_STATS=true \
DATASET_EXTERNAL_STATS_ROOT=/path/to/norm_stats \
bash launch/tbot_sa1_finetune_robotwin.sh
```

### Finetuning example

Use this script for a single LeRobot-v3.0 dataset. It defaults to delta actions.

```bash
POLICY_INIT_PATH=zaleni/TBot-SA1-Base \
DATASET_REPO_ID=/path/to/lerobot_v3.0_dataset \
ACTION_TYPE=delta \
USE_EXTERNAL_STATS=true \
bash launch/tbot_sa1_finetune.sh
```

For delta-action training, compute normalization statistics first:

```bash
python tools/compute_norm_stats_single.py \
  --repo_id /path/to/lerobot_v3.0_dataset \
  --action_mode delta \
  --chunk_size 50 \
  --output_dir norm_stats
```

### Multi-Dataset Pretraining

`launch/tbot_sa1_pretrain.sh` can discover datasets from multiple roots:
`INTERNDATA_ROOT`, `ROBOTWIN_ROOT`, `ROBOCHALLENGE_ROOT`, `AGIBOT_ROOT`, and
`EGODEX_LEROBOT_ROOT`.

```bash
ROBOTWIN_ROOT=/path/to/robotwin_lerobot_v3 \
EGODEX_LEROBOT_ROOT=/path/to/egodex_lerobot_v3 \
DATASET_EXTERNAL_STATS_ROOT=/path/to/norm_stats \
WEIGHT_RULES_PATH=configs/tbot_sa1_pretrain_data_config.yaml \
bash launch/tbot_sa1_pretrain.sh
```

Some other policies are also supported by this repository, training scripts are available in
`launch/supported_methods/`:

- `qwenaction_finetune.sh`
- `pi0_finetune.sh`
- `pi05_finetune.sh`
- `internvla_a1_3b_finetune.sh`
- `fastwam_finetune.sh`


## Acknowledgments

TBot-SA1 builds on the excellent work of the
[LeRobot](https://github.com/huggingface/lerobot),
[RoboTwin](https://github.com/RoboTwin-Platform/RoboTwin),
[Qwen3-VL](https://github.com/QwenLM/Qwen3-VL),
[Depth-Anything-3](https://github.com/ByteDance-Seed/Depth-Anything-3),
[InternVLA-A1](https://github.com/InternRobotics/InternVLA-A1), and
[FastWAM](https://github.com/yuantianyuan01/FastWAM). Some adapted policy scripts are kept in this repository to make reproduction and
ablation runs easier from the same codebase.

## Citation

<p align="center">
  <img src="assets/tongji-logo.png" alt="Tongji University" height="56">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/sii-logo.png" alt="Shanghai Innovation Institute" height="56">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/sig-logo.png" alt="Spatial Intelligence Group" height="56">
</p>
