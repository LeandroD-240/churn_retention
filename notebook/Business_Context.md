# Churn Prediction and Retention ROI Simulator

## Company Context

**VoxTel** is a mid-sized regional telecommunications provider serving approximately **500,000 postpaid subscribers** across three product lines: mobile plans, home broadband, and bundled OTT streaming packages. Operating in a saturated and highly competitive market, VoxTel has seen its monthly churn rate climb to **3.2%** over the last four quarters — more than double the industry benchmark of 1.5%.

Each churned subscriber represents not only lost Monthly Recurring Revenue (MRR) but also the sunk cost of customer acquisition (CAC), estimated at $180 per subscriber. At its current trajectory, the business is projected to lose an estimated **$28M in annualized revenue** if the churn trend is not reversed.

The leadership team has named customer retention a Tier-1 strategic priority. However, current retention campaigns are applied broadly and without targeting, resulting in a high cost-per-save and significant budget waste on customers who were never going to churn in the first place.

---

## Frame the Problem

VoxTel has been experiencing sustained churn across several consecutive quarters. The core challenge is twofold:

1. **Identify** which customers are likely to churn before they do.
2. **Act** on those predictions with the right retention strategy at the right time.

The company currently lacks a systematic, data-driven mechanism to prioritize which customers to target, leading to inefficient retention campaigns deployed indiscriminately across the entire subscriber base.

---

## The Root Cause (5 Why's)

1. **Why are customers churning?** Because of unidentified and varying reasons that the company often cannot acknowledge in time — such as competitive offers, service dissatisfaction, billing disputes, or life events.

2. **Why can't the company acknowledge these reasons?** Because it lacks the tools to recognize patterns in customer behavior that are predictive of churn before it actually happens.

3. **Why can't the company catch these patterns?** Because it has no automated technique or system that calls it to action. The company can offer discounts, place calls, or provide upgrades — but applying these strategies to every customer is prohibitively expensive.

4. **Why is it expensive to implement these strategies for every customer?** Because the company cannot differentiate customers who are likely to churn from those who are not, resulting in wasted spend on already-loyal subscribers.

**The root cause**, therefore, is the **absence of a predictive system** capable of identifying at-risk customers and enabling targeted, cost-efficient retention actions before churn occurs.

---

## KPIs

### 1. Customer Lifetime Value (CLV)

**Formula:**

```
CLV = (ARPU × Gross Margin %) / Monthly Churn Rate
```

Where:
- **ARPU** = Average Revenue Per User per month (e.g., $45)
- **Gross Margin %** = Revenue minus variable service costs, expressed as a percentage (e.g., 60%)
- **Monthly Churn Rate** = Fraction of active customers lost in a given month (e.g., 0.032)

**Example:** CLV = ($45 × 0.60) / 0.032 = **$843.75 per customer**

**Explanation:** CLV quantifies the total expected net revenue a customer generates over the entire duration of their relationship with the company. It serves as the anchor for every retention investment decision — it defines the upper bound of what the company should rationally spend to save a single customer. In this project, CLV is used to **prioritize intervention targets**: retaining a high-CLV subscriber justifies a costlier intervention (e.g., a personal retention call with a premium upgrade), while a low-CLV subscriber may only warrant a low-cost automated campaign.

---

### 2. Projected Savings (Retention ROI)

**Formula:**

```
Projected Savings = (TP × Rc × CLV) − (N_contacted × C_intervention)
```

Where:
- **TP** = True Positives: customers correctly identified as at-risk who were contacted
- **Rc** = Retention Conversion Rate: fraction of contacted at-risk customers who are successfully retained (e.g., 25%)
- **CLV** = Customer Lifetime Value (see above)
- **N_contacted** = Total customers contacted = TP + FP (True Positives + False Positives)
- **C_intervention** = Average cost per retention action (e.g., $15: agent time + offer cost)

**Example:** With TP = 1,200, Rc = 0.25, CLV = $843, N_contacted = 1,500, C_intervention = $15:
- Revenue saved = 1,200 × 0.25 × $843 = **$252,900**
- Campaign cost = 1,500 × $15 = **$22,500**
- **Net Projected Savings = $230,400 per campaign cycle**

**Explanation:** Projected Savings directly translates the model's predictive accuracy into business value. It captures the financial benefit of acting on the model's output while accounting for the full cost of the retention campaign. The better the model's **precision** (fewer False Positives), the lower the unnecessary intervention cost and the higher the net ROI. This KPI is the primary metric used to evaluate not just model performance in isolation, but the end-to-end **business performance** of the entire retention pipeline.

---

### 3. Revenue at Risk

**Formula:**

```
Revenue at Risk = Σ [ P(churn_i) × CLV_i ]   for all i in the active subscriber base
```

Where:
- **P(churn_i)** = Predicted churn probability for customer *i* (model output)
- **CLV_i** = Estimated Lifetime Value for customer *i*
- The sum runs across all N active subscribers

**Example:** A segment of 10,000 customers with an average P(churn) = 0.40 and an average CLV of $843 yields a Revenue at Risk of **$3.37M**.

**Explanation:** Revenue at Risk is a metric that aggregates expected revenue exposure across the entire subscriber base, weighted by each customer's individual churn probability and economic value. Unlike a binary churn flag, this measure uses the raw probability output of the model to express financial exposure as a continuous, monetized signal. It gives the **C-suite, Finance, and Risk teams** a single number summarizing how much revenue is currently "at risk" — enabling strategic decisions on how aggressively to deploy retention budgets. This KPI is updated on a rolling monthly basis as the model rescores the full subscriber base.

---

## Business Levers

Once at-risk customers are identified by the model, the following retention interventions can be deployed. Each lever is calibrated to the customer's **predicted risk tier** (Low: < 30%, Medium: 30–60%, High: > 60%) and estimated CLV, ensuring that intervention cost is proportional to the value at stake:

| Lever | Description | Target Segment |
|---|---|---|
| **Targeted Discount** | Offer a 10–20% plan reduction valid for 3 months | High churn probability, price-sensitive, mid CLV |
| **Proactive Retention Call** | A trained retention specialist contacts the customer to address pain points and present tailored offers | High CLV, high risk |
| **Service Upgrade** | Complimentary data boost, broadband speed tier upgrade, or OTT add-on at no extra cost for 2 months | Usage-driven churners with engagement drop |
| **Loyalty Program Enrollment** | Points-based rewards redeemable against bills, for tenure milestones and on-time payments | Long-tenure, mid-risk customers |
| **Contract Lock-In Incentive** | Discounted monthly rate in exchange for committing to a 12-month extension | Month-to-month subscribers at moderate risk |
| **Personalized Re-engagement Campaign** | Targeted SMS/email sequence based on individual usage patterns, preferences, and past interactions | Low-to-mid risk, high-volume segment |
| **Priority Technical Support** | Fast-track resolution of open service tickets or quality complaints | Churners driven by repeated service issues |

The model's churn probability score will be used to **segment customers into risk tiers**, and each tier will be assigned the appropriate lever (or combination of levers) based on cost-effectiveness and expected conversion rate.

---

## Prediction Horizon and Operational Timing

The model does not predict whether a customer will *eventually* churn at some point in the future. It predicts whether a customer is likely to churn **within the next 2 months from the scoring date**.

This distinction is intentional and has direct operational consequences. Retention campaigns are not instantaneous. Between the moment the model flags a customer as at-risk and the moment that customer actually receives an intervention, VoxTel's teams must complete several sequential steps:

| Operational Step | Estimated Time Required |
|---|---|
| Budget approval from Finance / Marketing leadership | 3–5 business days |
| Campaign design: offer selection, channel, creative assets | 5–7 business days |
| Execution: agent scheduling, SMS/email deployment, call queues | 3–5 business days |
| Customer response window: time for the subscriber to evaluate the offer | 7–14 days |
| **Total minimum lead time** | **~3 to 4 weeks** |

This means that if VoxTel's operational teams do not act on the model's output **within the first 2–3 weeks of each monthly scoring cycle**, they risk a compounding failure: the model correctly identified an at-risk customer, a budget was allocated, a campaign was planned — but the customer canceled before the intervention ever reached them. This is a **silent operational failure**: it does not register as a model error, yet it still costs the business the full CLV of that subscriber.

### The Contractual Commitment

The 2-month prediction horizon represents a **service-level agreement between the Data Science team and VoxTel's operational units**:

- **The DS team commits** to delivering a scored, risk-tiered customer list at the start of each monthly cycle, with sufficient lead time for teams to act.
- **Operations, Marketing, and Customer Success commit** to launching campaigns within the first 2–3 weeks of receiving that list — before the churn window closes.

If this operational commitment is not honored, the model's accuracy becomes irrelevant. Early identification only creates value when it is followed by timely action.

---

## Is This a Data Science Problem?

Yes. The project satisfies each of the qualifying criteria for a Machine Learning intervention:

| Criterion | Justification |
|---|---|
| **Is there enough data?** | Yes, VoxTel holds 24+ months of historical subscriber data: demographics, contract type, monthly billing amounts, service usage (call minutes, data consumption, SMS), payment history, customer support interactions, plan changes, and labeled churn events. The dataset contains approximately 5,000 confirmed observations — sufficient for robust supervised classification. |
| **Is the pattern complex?** | Yes, Churn is not triggered by a single, obvious rule. It results from a combination of behavioral, financial, and relational signals that interact in non-linear ways — precisely the kind of problem where machine learning outperforms manual rule-based systems. |
| **Does a better prediction lead to a better decision?** | Yes, A targeted model allows the company to deploy retention campaigns exclusively on customers most likely to churn, eliminating wasted spend on loyal subscribers and enabling personalized intervention strategies per risk tier. |
| **Can the output be operationalized?** | Yes, The model's output (a churn probability score per customer) can be consumed by multiple departments: the **Marketing team** for campaign targeting, the **Customer Success team** for prioritizing outbound calls, and the **C-suite and Finance teams** for monitoring Revenue at Risk through a real-time dashboard. |
| **Is the impact measurable against the KPI?** | Yes, he model's business impact is directly quantifiable via Projected Savings, tracked month-over-month. An A/B testing framework — where a random holdout group receives no retention intervention — can isolate the model's incremental contribution to churn reduction, providing clean, causal evidence of ROI. |

---

## Analytical Approach

This project adopts a **predictive, prescriptive, and evaluative** approach across three interconnected layers:

1. **Predictive layer** — A supervised classification model (evaluated across Logistic Regression, Gradient Boosting or ensemble methods) trained on historical subscriber behavior to produce a churn probability score for each active customer. The prediction target is explicitly defined as **churn within the next 2 months**, establishing the operational window within which retention actions must be executed (see *Prediction Horizon and Operational Timing* above).

2. **Prescriptive layer** — A decision engine that uses the churn probability score and individual CLV estimate to assign each customer to a risk tier and recommend the optimal retention lever (see Business Levers above).

3. **Evaluation layer** — A Retention ROI Simulator that quantifies the financial impact of the retention campaign in terms of Projected Savings, modeling the tradeoff between model precision, intervention cost, and revenue retained.

This end-to-end framework ensures the project is not merely a modeling exercise but a complete **business decision support system** aligned with VoxTel's strategic retention objectives.
