# Dataset and Scripts: Comparing Human Visual Search and Multimodal LLM Reasoning Strategies in Map Reading

---

Scripts of data processing and visualizing are included. 

## Main scripts

---

Main scripts and their explanations are listed below.

| Script Path          | Script description                                                                                                                                                                                                                                                                 |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `./1auto_read.py`    | Automatically call the LLM APIs to send requests and retrieve responses. Configurations are set in `./tools/cfg.py`.  The API keys are configured in `./tools/api.py`.                                                                                                             |
| `./2data_process.py` | Calculate trajectories; extract data for SPSSPRO calculation.                                                                                                                                                                                                                      |
| `./3draw.py`         | Create visualization charts.                                                                                                                                                                                                                                                       |
| `./3traj_compare.py` | Compare trajectories within human participants, within each LLM, and between LLMs.                                                                                                                                                                                                 |
| `./4tst.ipynb`       | Other data processing and visualization. Including calculating accuracy rates by task type, computing local patterns and creating visual charts, creating visual charts for semantic codes, generating transition matrices, and creating visual charts for trajectory comparisons. |

## Installation

---

This project requires Python 3.12 or later.

1. Clone or download this repository.

2. Install the required dependencies:
   
   ```
   pip install -r requirements.txt
   ```

3. Run the Python scripts as described in the above section.

## Run scripts

---

Run the code listed in the “Main scripts” module. **The scripts are suggested to be run in order, because later scripts might require output data from former scripts.** 

For example, `1auto_read.py` should be run before `2data_process.py`. The scripts `3draw.py` and `3traj_compare.py` do not interfere with each other; you only need to run the former two scripts to run either of them.

## Inputs

---

| File path                     | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| `./data/all_code.csv`         | Grid AOIs and semantic codes of all LLMs and participants during map tasks. |
| `./data/filtered_metrics.csv` | Raw eye-tracking data collected from participants.                          |

## Outputs

---

| Script             | Output paths                                                                                                                                                                                                                                                                     | Description                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `1auto_read.py`    | `./test_result/*.xlsx`                                                                                                                                                                                                                                                           | Received answers from LLMs.                           |
| `2data_process.py` | `./output/all_report.csv`, `./output/all_traj.csv`, `./output/report_spss.csv`, `./output/report_spss/*.csv`                                                                                                                                                                     | Statistical data for visualization or analysis.       |
| `3draw.py`         | `./output/pics/*.png`, `./output/pics/heatmap/by_respondent/*.png`, `./output/pics/heatmap/by_respondent_correctness/*.png`, `./output/pics/heatmap/by_respondent_task/*.png`, `./output/pics/heatmap/by_respondent_tasktype1/*.png`, `./output/pics/heatmap/by_tasktype1/*.png` | Visualization graphics.                               |
| `3traj_compare.py` | `./output/traj_compare.csv`, `./output/traj_compare_ai.csv`, `./output/traj_compare_human.csv`                                                                                                                                                                                   | Trajectory comparie results.                          |
| `4tst.ipynb`       | `./output/local_pattern.csv`, `./output/for_spss/pattern/*.csv`, `./output/for_spss/semantic/*.csv`, `./output/for_spss/semantic_0/*.csv`, `./output/for_spss/semantic_1/*.csv`, `./output/transfer_matrix/pattern/*.png`, `./output/transfer_matrix/semantic/*.png`             | Local pattern data, and other visualization graphics. |
