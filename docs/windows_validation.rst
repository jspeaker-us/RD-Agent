=====================================
Windows Native Validation Status
=====================================

Scope
=====

This page documents the current Windows-native validation status for this local fork. The upstream project still primarily targets Linux. The Windows work described here focuses on private, local Windows usage with Conda environments instead of WSL, virtual machines, or Docker fallback.

The validated machine used:

- Windows with PowerShell.
- Miniforge installed at ``C:\ProgramData\miniforge3``.
- RD-Agent source checkout at ``D:\win\AIBaff_win\RD-Agent``.
- Main RD-Agent Conda environment named ``rdagent-win``.
- Qlib execution Conda environment named ``rdagent4qlib``.
- Qlib CN daily data installed at ``C:\Users\speaker\.qlib\qlib_data\cn_data``.
- Data Science smoke fixture under ``git_ignore_folder\windows_ds_smoke``.

Validated Features
==================

The following features have been reproduced on Windows native Conda.

Core Environment
----------------

- Editable RD-Agent install in ``rdagent-win``.
- Qlib execution through ``QlibCondaEnv`` in ``rdagent4qlib``.
- LiteLLM-compatible chat completion using an OpenAI-compatible provider.
- Local hash embedding through ``EMBEDDING_MODEL=local/hash-embedding``.
- Health check without Docker.
- Windows path handling for local execution, Qlib execution, and workspace artifacts.
- Native Windows ``LocalEnv`` command execution.
- Data Science Conda execution using a configurable Conda environment name.

Quantitative Finance Workflows
------------------------------

The following commands completed one loop and produced Qlib result artifacts.

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_quant --loop-n 1

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_factor --loop-n 1

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_model --loop-n 1

Validated outputs include:

- ``qlib_res.csv``
- ``ret.pkl``
- ``combined_factors_df.parquet`` for combined-factor runs
- ``model.py`` for model-generation runs
- generated factor/model workspaces under ``git_ignore_folder\RD-Agent_workspace``

Representative successful result directories observed during validation:

- ``git_ignore_folder\RD-Agent_workspace\5c283ab988c847388ddfc1c1924c132d``
- ``git_ignore_folder\RD-Agent_workspace\dbcde018872e47a5a06078f3df9dc6cc``
- ``git_ignore_folder\RD-Agent_workspace\930c7c5735cb4df99f81011a85f199d0``
- ``git_ignore_folder\RD-Agent_workspace\4d5dc53ebf1f4eddb4316f89ea104d20``

Finance Multi-Loop Smoke
------------------------

``fin_factor`` was also started with two loops:

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_factor --loop-n 2

The run produced an additional Qlib result directory and entered the second-loop factor workspace creation path before the external tool timeout stopped observation. This validates state handoff into the second loop, but it is not treated as a completed long-run benchmark.

General Data Science Workflow
-----------------------------

The General Data Science workflow completed one loop on a local Windows smoke fixture with Conda execution.

Validated command shape:

.. code-block:: powershell

   $env:DS_LOCAL_DATA_PATH="D:\win\AIBaff_win\RD-Agent\git_ignore_folder\windows_ds_smoke"
   $env:DS_SCEN="rdagent.scenarios.data_science.scen.DataScienceScen"
   $env:DS_CODER_COSTEER_ENV_TYPE="conda"
   $env:DS_CODER_COSTEER_CONDA_ENV_NAME="rdagent-win"
   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent data_science --competition windows-ds-smoke --loop-n 1 --timeout 30m

Observed result:

- ``Workflow Progress: 100%``.
- scenario initialization completed.
- LLM competition parsing completed.
- Conda workspace execution completed.
- submission validation completed.
- grading completed with JSON output.

Kaggle-Compatible Offline Workflow
----------------------------------

The current CLI routes Kaggle-style tasks through ``rdagent data_science``. For private Windows-native use, the validated path is offline/prepared-data usage rather than live Kaggle API download.

Validated behavior:

- If ``<DS_LOCAL_DATA_PATH>\<competition>`` already exists and is non-empty, data download is skipped.
- ``description.md`` is loaded locally instead of requiring browser crawling.
- missing Kaggle credentials do not block metric direction when the LLM-derived direction is available.
- zip extraction uses safe path validation.
- submission validation and grading work on the local fixture.

This validates the Windows-native Kaggle-compatible execution layer for prepared local data. Live Kaggle API download, joining competitions, leaderboard lookup, and online submission remain intentionally outside this private Windows scope.

Research Copilot and Report Ingestion
-------------------------------------

The report/PDF ingestion layer was validated with a generated one-page PDF fixture:

- ``load_and_process_pdfs_by_langchain`` loaded the PDF.
- ``extract_first_page_screenshot_from_pdf`` produced an image.
- ``rdagent general_model --help`` loaded the CLI path.
- ``rdagent fin_factor_report --help`` loaded the CLI path.
- direct Fire entrypoints for ``general_model.py`` and ``factor_from_report.py`` loaded.

This validates Windows PDF parsing and entrypoint readiness. End-to-end paper/report-to-implemented-model or report-to-factor R&D was not run because it is LLM-heavy and can cascade into full model/factor development loops.

Fine-Tuning Boundary
--------------------

Fine-tuning was validated only at the Windows boundary level:

- ``rdagent llm_finetune --help`` loaded.
- fine-tuning settings imported.
- registered datasets imported.
- Windows cleanup no longer uses ``rm -rf`` in native Conda mode.

Full fine-tuning training/evaluation is intentionally not part of this Windows-native private scope because the stack is Docker/GPU/Linux-oriented: ``flash-attn``, ``deepspeed``, ``bitsandbytes``, ``vllm``, CUDA PyTorch, OpenCompass, model downloads, and long training runs.

Validated Setup Steps
=====================

Create Environments
-------------------

Create the main RD-Agent environment.

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" create -n rdagent-win python=3.10

Install RD-Agent from the source checkout.

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win python -m pip install -e .

Create or prepare the Qlib environment through RD-Agent, or create a Conda environment named ``rdagent4qlib`` with the required Qlib dependencies. The validated Qlib environment included:

- ``pyqlib 0.9.8.dev26``
- ``torch 2.11.0+cpu``
- ``catboost``
- ``xgboost``
- ``tables``
- working ``qrun --help``

Configure Environment Variables
-------------------------------

Use a local ``.env`` file. Do not commit API keys.

.. code-block:: properties

   OPENAI_API_BASE=<your_openai_compatible_base_url>
   OPENAI_API_KEY=<your_api_key>
   CHAT_MODEL=gpt-5.5
   LITELLM_CHAT_MODEL=gpt-5.5
   REASONING_EFFORT=high
   LITELLM_REASONING_EFFORT=high
   CHAT_TEMPERATURE=1
   LITELLM_CHAT_TEMPERATURE=1
   EMBEDDING_MODEL=local/hash-embedding
   LITELLM_EMBEDDING_MODEL=local/hash-embedding
   MODEL_COSTEER_ENV_TYPE=conda
   FACTOR_COSTEER_ENV_TYPE=conda
   DS_CODER_COSTEER_ENV_TYPE=conda
   DS_CODER_COSTEER_CONDA_ENV_NAME=rdagent-win
   QLIB_DOCKER_ENABLE_GPU=False
   RD_AGENT_STEP_SEMAPHORE=1

The local validation used an OpenAI-compatible chat provider and ``local/hash-embedding`` because the provider did not expose a compatible embedding endpoint.

Prepare Qlib Data
-----------------

Install Qlib CN daily data under the default user data directory.

.. code-block:: text

   C:\Users\speaker\.qlib\qlib_data\cn_data

The validated directory contained:

- ``calendars``
- ``features``
- ``instruments``

The data was validated with ``qlib.init`` and a calendar query.

Generate factor source data if missing.

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent4qlib python rdagent\scenarios\qlib\experiment\factor_data_template\generate.py

Expected generated files:

- ``rdagent\scenarios\qlib\experiment\factor_data_template\daily_pv_all.h5``
- ``rdagent\scenarios\qlib\experiment\factor_data_template\daily_pv_debug.h5``

Run Health Check
----------------

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent health_check --no-check-docker

Expected result:

- embedding test passed
- chat test passed
- UI port check completed

Run Quant Workflows
-------------------

Run the three validated workflows from the repository root.

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_quant --loop-n 1
   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_factor --loop-n 1
   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent fin_model --loop-n 1

Verify output artifacts.

.. code-block:: powershell

   Get-ChildItem "git_ignore_folder\RD-Agent_workspace" -Recurse -Filter qlib_res.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 10 FullName,LastWriteTime,Length

Run Data Science Smoke
----------------------

Prepare a small local fixture with this structure:

.. code-block:: text

   git_ignore_folder\windows_ds_smoke
   ├── windows-ds-smoke
   │   ├── description.md
   │   ├── train.csv
   │   ├── test.csv
   │   └── sample_submission.csv
   └── eval
       └── windows-ds-smoke
           ├── valid.py
           ├── grade.py
           └── submission_test.csv

Run:

.. code-block:: powershell

   $env:DS_LOCAL_DATA_PATH="D:\win\AIBaff_win\RD-Agent\git_ignore_folder\windows_ds_smoke"
   $env:DS_SCEN="rdagent.scenarios.data_science.scen.DataScienceScen"
   $env:DS_CODER_COSTEER_ENV_TYPE="conda"
   $env:DS_CODER_COSTEER_CONDA_ENV_NAME="rdagent-win"
   $env:DS_SAMPLE_DATA_BY_LLM="True"
   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent data_science --competition windows-ds-smoke --loop-n 1 --timeout 30m

Install ``coverage`` in the Conda environment if the Data Science runtime check reports it missing:

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win python -m pip install coverage

Run PDF/Report Smoke
--------------------

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win python -c "from rdagent.components.document_reader.document_reader import load_and_process_pdfs_by_langchain, extract_first_page_screenshot_from_pdf; p=r'git_ignore_folder\windows_report_smoke.pdf'; docs=load_and_process_pdfs_by_langchain(p); img=extract_first_page_screenshot_from_pdf(p); print(len(docs), img.size)"

Run Fine-Tuning Boundary Smoke
------------------------------

.. code-block:: powershell

   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win rdagent llm_finetune --help
   & "C:\ProgramData\miniforge3\Scripts\conda.exe" run -n rdagent-win python -c "from rdagent.scenarios.finetune.datasets import DATASETS; from rdagent.app.finetune.llm.conf import FT_RD_SETTING; from rdagent.components.coder.finetune.conf import FTCoderCoSTEERSettings; print(sorted(DATASETS)); print(FT_RD_SETTING.file_path); print(FTCoderCoSTEERSettings().env_type)"

Known Windows-Specific Changes
==============================

The validated Windows path depends on these local changes:

- Local and Conda execution avoid POSIX ``/bin/sh`` on Windows.
- Windows command timeout uses ``subprocess.communicate(timeout=...)`` instead of POSIX ``timeout``.
- Conda execution uses ``CONDA_EXE`` and ``python -m pip``.
- Qlib data generation can run under Windows ``multiprocessing`` spawn.
- Workspace file linking falls back from hardlink to copy when needed.
- Qlib factor execution uses the Qlib Conda environment on Windows.
- Model training hyperparameters and PyTorch DataLoader workers are capped on Windows to avoid spawn/shared-memory failures during Qlib model runs.
- LiteLLM settings logs are redacted for key-like values.
- Health check supports ``local/hash-embedding`` and no-Docker validation.
- Data Science cleanup, backup, validation, and grading avoid POSIX-only ``rm``, ``cp``, ``tee``, and ``chmod`` on Windows.
- Data Science Conda environment name can be configured with ``DS_CODER_COSTEER_CONDA_ENV_NAME``.
- Kaggle-compatible offline prepared-data runs skip download and safely extract zip files.
- Fine-tuning workspace cleanup avoids ``rm -rf`` on Windows native Conda.
- Shared runtime checks avoid host Windows ``which``/shell fallback noise.

Out Of Scope Or Partial
=======================

The following features are intentionally outside this private Windows-native scope or only partially validated.

Docker-Based Execution on Windows
---------------------------------

Docker Desktop was not used as the fallback execution route. The validated path uses Conda for the finance workflows. Docker daemon availability, Windows Docker volume behavior, and GPU Docker execution remain unvalidated.

Live Kaggle Service Integration
-------------------------------

Offline/prepared-data Kaggle-compatible behavior is validated through ``rdagent data_science``. Live Kaggle API download, joining competitions, leaderboard retrieval, browser crawling, and online submission are not required for private local use and remain unvalidated.

Fine-Tuning Scenarios
---------------------

Fine-tuning CLI/config/import and Windows cleanup boundaries are validated. Full training, GPU execution, model/dataset downloads, distributed training, and benchmark evaluation remain unvalidated and are not part of the private Windows-native target.

Web UI and Server UI
--------------------

The health check verified that the default UI port was free, but ``rdagent ui`` and ``rdagent server_ui`` were not run as part of this validation.

Research Copilot and Report Workflows
-------------------------------------

PDF parsing and report CLI entrypoints are validated. End-to-end paper/report-to-implementation loops remain partial because they can invoke full LLM-heavy model/factor development.

Multi-Loop Long Runs
--------------------

Finance second-loop state handoff was observed through a ``fin_factor --loop-n 2`` run that produced a new Qlib result and entered second-loop factor work before external observation timed out. High-parallelism, long-running model searches, and completed multi-hour benchmark runs remain unvalidated.

Fresh-Machine Reproducibility
-----------------------------

The current status is local functional validation, not a clean-room installer. A fresh Windows machine may still need manual setup for:

- Miniforge installation.
- Qlib CN data download.
- Qlib dependency resolution.
- API provider configuration.
- local disk paths.

Operational Notes
=================

- Do not commit ``.env`` files or API keys.
- Do not commit generated Qlib data, workspaces, prompt caches, or result artifacts unless explicitly needed for a fixture.
- PowerShell quoting differs from Bash; prefer single-line ``python -c`` snippets or script files.
- ``conda run ... python -c`` on Windows does not support arguments containing newlines.
- The Windows model training cap is intended for smoke validation, not maximum research quality.
