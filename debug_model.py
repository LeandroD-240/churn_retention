import pickle
import pandas as pd
import sys
from pathlib import Path

DROP_COLS = [
    "churned", "customer_id", "total_charges", "clv_estimated",
    "has_streaming_addon", "tenure_months", "payment_method",
    "monthly_charges", "retention_action",
]

DATA_PATH = Path("data/voxtel_data.csv")
MODEL_PATH = Path("data/champion.pkl")


def load_model(model_path: Path = MODEL_PATH):
    with model_path.open("rb") as f:
        return pickle.load(f)


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(data_path)


def debug_model() -> dict:
    model = load_model()
    df = load_data()

    feature_cols = [c for c in df.columns if c not in DROP_COLS]
    X = df[feature_cols].head(5)
    probs = model.predict_proba(X)[:, 1]

    return {
        "model_type": str(type(model)),
        "data_shape": df.shape,
        "feature_cols": feature_cols,
        "sample_dtypes": X.dtypes.astype(str).to_dict(),
        "predicted_probabilities": probs.tolist(),
        "sample_row": X.head(1).to_dict(orient="records"),
    }


if __name__ == "__main__":
    try:
        result = debug_model()
        print("Model debug result:")
        for key, value in result.items():
            print(f"{key}: {value}")
    except Exception as exc:
        print("Model diagnostics failed:", repr(exc))
        sys.exit(1)
