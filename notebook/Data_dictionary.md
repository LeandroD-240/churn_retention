# Data Dictionary

## Dictionary Table

| Field | Type | Description |
|---|---|---|
|customer_id|Integer|Unique identifier for the customer|
|tenure_months|Integer|How long the customer has been subscribed. Short tenure + churn = early dropout signal.|
|monthly_charges|Float|Monthly fee paid. High charge + low engagement often drives churn.|
|contract_type|Categorical|Month-to-month, one-year, two-year. The single strongest churn predictor in most datasets.|
|num_support_tickets|Integer|Tickets opened in the last 90 days. Proxy for friction/dissatisfaction.|
|data_usage_gb|Float|Monthly data consumed in gigabytes, averaged over the last 3 months. Low and declining usage is a disengagement signal ahead of churn, especially for broadband subscribers.|
|has_streaming_addon|Binary|1 = subscribed to the OTT streaming bundle, 0 = mobile/broadband only. Customers with multiple services bundled are significantly more costly to replace, reducing churn likelihood.|
|last_login_days_ago|Integer|Days since last platform activity. Disengagement signal before churn happens.|
|plan_type|Categorical|Basic, Standard, Premium. Used to segment retention actions by customer value tier.|
|payment_method|Categorical|Credit card, bank transfer, etc. Electronic payments correlate with lower churn.|
|payment_delay_days|Integer|Average number of days late on payments in the last 6 months. Financial friction signal — repeated delays suggest dissatisfaction or financial stress, both churn precursors.|
|clv_estimated|Float|Calculated as monthly_charges × expected_remaining_months. This is what powers the ROI simulator.|
|churned|Binary|1 = churned, 0 = active. The target variable for the classifier.|
|retention_action|Categorical|Discount, account manager call, plan upgrade. Added during simulation — not in raw data.|

## Samples

|customer_id|tenure_months|monthly_charges|contract_type|num_support_tickets|data_usage_gb|has_streaming_addon|last_login_days_ago|plan_type|payment_method|payment_delay_days|clv_estimated|churned|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|C-00841|6|79.90|Month-to-month|4|1.2|0|38|Standard|Credit card|12|479.40|1|
|C-01293|31|44.50|One-year|0|18.7|1|3|Basic|Bank transfer|0|1379.50|0|