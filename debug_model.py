import pickle
import pandas as pd
import sys

DROP_COLS = [
    "churned", "customer_id", "total_charges", "clv_estimated",
    "has_streaming_addon", "tenure_months", "payment_method",
    "monthly_charges", "retention_action",
]

print("Loading model...")
with open("data/champion.pkl", "rb") as f:
    model = pickle.load(f)
print("Model loaded:", type(model))

print("Loading CSV...")
df = pd.read_csv("data/voxtel_data.csv")
print("CSV rows, cols:", df.shape)

feature_cols = [c for c in df.columns if c not in DROP_COLS]
print("Feature cols sample:", feature_cols[:10])

X = df[feature_cols].head(5)
print("X dtypes:\n", X.dtypes)

try:
    probs = model.predict_proba(X)[:, 1]
    print("Predicted probabilities:", probs)
except Exception as e:
    print("predict_proba raised:", repr(e))
    sys.exit(1)

print("Done")
