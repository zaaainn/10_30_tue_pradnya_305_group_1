"""Apply the saved Random Forest models to labeled or new scenario records."""

import argparse
from pathlib import Path

import pandas as pd

from diagnosis import DEFAULT_MODEL_PATH, load_model, predict_records
from generate_labeled_dataset import DEFAULT_OUTPUT as DEFAULT_DATASET


ROOT = Path(__file__).resolve().parent
DEFAULT_PREDICTIONS = ROOT / "outputs" / "random_forest_predictions.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict scenario condition and fault zone.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_PREDICTIONS)
    args = parser.parse_args()

    data = pd.read_csv(args.dataset)
    model_bundle = load_model(args.model)
    predictions = predict_records(data, model_bundle=model_bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output, index=False, float_format="%.6f")
    print(f"Saved {len(predictions)} predictions to {args.output}")
    print("Predicted condition counts:")
    print(predictions["Predicted_Condition"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
