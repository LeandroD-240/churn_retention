import pandas as pd
import pickle

df = pd.read_csv('data/voxtel_data.csv')

DROP_COLS = ["churned", "customer_id", "total_charges", "clv_estimated", 
"has_streaming_addon", "tenure_months", "payment_method", "monthly_charges"]

df.drop(columns=DROP_COLS, inplace=True)

sample = df.sample(n=1, random_state=42)

with open('data/champion.pkl', 'rb') as f:
    model = pickle.load(f)

try:
    result = model.predict(sample)
    print(result)
except Exception as e:
    print(f"Error occurred: {e}")