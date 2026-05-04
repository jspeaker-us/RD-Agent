import pickle
from pathlib import Path

import pandas as pd

REQUIRED_OBJECTS = [
    "portfolio_analysis/report_normal_1day.pkl",
    "pred.pkl",
]
REQUIRED_METRICS = [
    "IC",
    "1day.excess_return_with_cost.annualized_return",
    "1day.excess_return_with_cost.max_drawdown",
]


def validate_required_metrics(metrics, context):
    if metrics.empty:
        raise RuntimeError(f"{context} has no metrics; refusing to write qlib_res.csv.")
    missing_metrics = [metric for metric in REQUIRED_METRICS if metric not in metrics.index]
    if missing_metrics:
        raise RuntimeError(f"{context} is missing required metrics: {missing_metrics}")


def artifact_exists(recorder, artifact_path):
    parent = str(Path(artifact_path).parent).replace("\\", "/")
    name = Path(artifact_path).name
    try:
        artifacts = recorder.list_artifacts(None if parent == "." else parent)
    except Exception:
        return False
    return artifact_path in artifacts or name in artifacts


def validate_required_artifacts(recorder):
    missing_objects = [obj for obj in REQUIRED_OBJECTS if not artifact_exists(recorder, obj)]
    if missing_objects:
        raise FileNotFoundError(f"Latest Qlib recorder {recorder} is missing required artifacts: {missing_objects}")


import qlib
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

qlib.init()

from qlib.workflow import R

# here is the documents of the https://qlib.readthedocs.io/en/latest/component/recorder.html

# TODO: list all the recorder and metrics

# Assuming you have already listed the experiments
experiments = R.list_experiments()

# Iterate through each experiment to find the latest recorder
experiment_name = None
latest_recorder = None
for experiment in experiments:
    recorders = R.list_recorders(experiment_name=experiment)
    for recorder_id in recorders:
        if recorder_id is not None:
            experiment_name = experiment
            recorder = R.get_recorder(recorder_id=recorder_id, experiment_name=experiment)
            end_time = recorder.info["end_time"]
            try:
                # Check if the recorder has a valid end time
                if end_time is not None:
                    if latest_recorder is None or end_time > latest_recorder.info["end_time"]:
                        latest_recorder = recorder
                else:
                    print(f"Warning: Recorder {recorder_id} has no valid end time")
            except Exception as e:
                print(f"Error: {e}")

# Check if the latest recorder is found
if latest_recorder is None:
    raise RuntimeError("No Qlib recorders found; qrun did not produce MLflow artifacts.")
else:
    print(f"Latest recorder: {latest_recorder}")

    # Load the specified file from the latest recorder
    metrics = pd.Series(latest_recorder.list_metrics())
    validate_required_metrics(metrics, f"Latest Qlib recorder {latest_recorder}")

    output_path = Path(__file__).resolve().parent / "qlib_res.csv"
    metrics.to_csv(output_path)

    print(f"Output has been saved to {output_path}")

    validate_required_artifacts(latest_recorder)

    ret_data_frame = latest_recorder.load_object("portfolio_analysis/report_normal_1day.pkl")
    ret_data_frame.to_pickle("ret.pkl")
