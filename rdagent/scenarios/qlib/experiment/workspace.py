import re
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

from rdagent.components.coder.model_coder.conf import MODEL_COSTEER_SETTINGS
from rdagent.core.experiment import FBWorkspace
from rdagent.log import rdagent_logger as logger
from rdagent.utils.env import QlibCondaConf, QlibCondaEnv, QTDockerEnv

REQUIRED_METRICS = [
    "IC",
    "1day.excess_return_with_cost.annualized_return",
    "1day.excess_return_with_cost.max_drawdown",
]


class QlibFBWorkspace(FBWorkspace):
    def __init__(self, template_folder_path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.inject_code_from_folder(template_folder_path)

    def _qlib_env(self, run_env: dict) -> dict:
        env = dict(run_env)
        if MODEL_COSTEER_SETTINGS.env_type == "docker":
            return env
        workspace = self.workspace_path.resolve()
        try:
            in_git_repo = (
                subprocess.run(
                    ["git", "-C", str(workspace), "rev-parse", "--is-inside-work-tree"],
                    capture_output=True,
                    check=False,
                ).returncode
                == 0
            )
        except FileNotFoundError:
            in_git_repo = True
        if not in_git_repo:
            # Qlib/MLflow logs git diff/status on every run. In generated Windows workspaces
            # that are not git repos this creates noisy, harmless failures; point git at the
            # parent repo if available so MLflow logging still works without treating the
            # temporary workspace itself as a broken repository.
            parent_repo = Path(__file__).resolve().parents[4]
            if (parent_repo / ".git").exists():
                env.setdefault("GIT_DIR", str(parent_repo / ".git"))
                env.setdefault("GIT_WORK_TREE", str(parent_repo))
        return env

    def _read_qlib_result(self, qlib_res_path: Path) -> pd.Series | None:
        if not qlib_res_path.exists():
            logger.error(f"Qlib result file is missing: {qlib_res_path}")
            return None
        if qlib_res_path.stat().st_size == 0:
            logger.error(f"Qlib result file is empty: {qlib_res_path}")
            return None
        try:
            result_df = pd.read_csv(qlib_res_path, index_col=0)
        except EmptyDataError:
            logger.error(f"Qlib result file has no parseable metrics: {qlib_res_path}")
            return None
        if result_df.empty or result_df.shape[1] == 0:
            logger.error(f"Qlib result file has no metrics: {qlib_res_path}")
            return None
        result = result_df.iloc[:, 0]
        if result.empty or result.isna().all():
            logger.error(f"Qlib result metrics are empty or all NaN: {qlib_res_path}")
            return None
        missing_metrics = [metric for metric in REQUIRED_METRICS if metric not in result.index]
        if missing_metrics:
            logger.error(f"Qlib result file {qlib_res_path} is missing required metrics: {missing_metrics}")
            return None
        return result

    def execute(self, qlib_config_name: str = "conf.yaml", run_env: dict = {}, *args, **kwargs) -> str:
        if MODEL_COSTEER_SETTINGS.env_type == "docker":
            qtde = QTDockerEnv()
        elif MODEL_COSTEER_SETTINGS.env_type == "conda":
            qtde = QlibCondaEnv(conf=QlibCondaConf())
        else:
            logger.error(f"Unknown env_type: {MODEL_COSTEER_SETTINGS.env_type}")
            return None, "Unknown environment type"
        qtde.prepare()
        qlib_run_env = self._qlib_env(run_env)

        # Run the Qlib backtest
        execute_qlib_log = qtde.check_output(
            local_path=str(self.workspace_path),
            entry=f"qrun {qlib_config_name}",
            env=qlib_run_env,
        )
        logger.log_object(execute_qlib_log, tag="Qlib_execute_log")

        execute_log = qtde.check_output(
            local_path=str(self.workspace_path),
            entry="python read_exp_res.py",
            env=qlib_run_env,
        )

        quantitative_backtesting_chart_path = self.workspace_path / "ret.pkl"
        if quantitative_backtesting_chart_path.exists():
            ret_df = pd.read_pickle(quantitative_backtesting_chart_path)
            logger.log_object(ret_df, tag="Quantitative Backtesting Chart")
        else:
            logger.error(
                "Qlib quantitative backtesting artifact is missing: "
                f"{quantitative_backtesting_chart_path}. read_exp_res.py output:\n{execute_log}"
            )
            return None, execute_qlib_log + "\n" + execute_log

        qlib_res_path = self.workspace_path / "qlib_res.csv"
        result = self._read_qlib_result(qlib_res_path)
        if result is None:
            return None, execute_qlib_log + "\n" + execute_log

        # Here, we ensure that the qlib experiment has run successfully before extracting information from execute_qlib_log using regex; otherwise, we keep the original experiment stdout.
        pattern = r"(Epoch\d+: train -[0-9\.]+, valid -[0-9\.]+|best score: -[0-9\.]+ @ \d+ epoch)"
        matches = re.findall(pattern, execute_qlib_log)
        execute_qlib_log = "\n".join(matches)
        return result, execute_qlib_log
