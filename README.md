# Churn retention and ROI simulator — VoxTel Telecom

![Status](https://img.shields.io/badge/Status-Finished-BEEF9E?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-A188A6?style=flat-square)
![Python](https://img.shields.io/badge/Python-v3.11-01386A?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-v3.0.3-6f42c1?style=flat&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit%20Learn-v1.6.1-f7931e?style=flat&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-v6.9.0-0b3d91?style=flat&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.59.2-ff4b4b?style=flat&logo=streamlit&logoColor=white)

---

## Index

A

---

## Description

### Context and Problem

**VoxTel** is a ficticial mid-sized regional telecommunications provider serving approximately 500,000 postpaid subscribers across mobile plans, home broadband, and bundled OTT streaming packages. Operating in a saturated, highly competitive market, VoxTel has seen its monthly churn rate climb to **3.2%** — more than double the industry benchmark of 1.5% — putting an estimated **$28M in annualized revenue** at risk if the trend continues.

The core issue isn't a lack of retention tools. VoxTel can already offer discounts, upgrades, or personal outreach — but applying these to the entire subscriber base is prohibitively expensive, and today's campaigns are deployed broadly with no way to tell which customers are actually at risk. The company has never lacked the *means* to retain customers; it has lacked the ability to **identify who needs to be retained, and when**.

This is fundamentally a data problem: with 24+ months of behavioral, financial, and engagement data available per subscriber, and no simple rule capable of separating a loyal customer from one about to leave, the pattern is complex enough to justify a machine learning approach — and predictable enough that a better forecast directly translates into a better, cheaper, more targeted business decision.

### Solution Implemented

The project follows the full **CRISP-DM** methodology, translating a broad retention problem into a deployable decision-support system built on two connected layers:

**Predictions.** A binary classification model (Logistic Regression, selected via GridSearchCV after benchmarking against a baseline) scores every subscriber with the probability they will churn **within the next 2 months** — a deliberately short, operationally realistic window rather than an open-ended "will this customer ever leave" forecast. Each subscriber is segmented into a **risk tier** (Low / Medium / High) based on that probability, and model behavior is explained end-to-end using permutation importance and SHAP (bar + beeswarm), so every prediction is auditable, not just accurate.

**ROI Simulation.** A prescriptive layer turns each risk tier into a recommended retention lever (proactive call, targeted discount, contract lock-in, service upgrade, etc.), calibrated by the subscriber's estimated **Customer Lifetime Value (CLV)** so that costlier interventions are reserved for the customers actually worth saving. The financial impact of any campaign is then quantified through three core KPIs — **CLV**, **Revenue at Risk** (Σ P(churn) × CLV), and **Projected Savings** ((TP × conversion rate × CLV) − campaign cost) — giving Marketing, Customer Success, and Finance teams a single, defensible number to plan and evaluate retention spend against.

The system also encodes an operational constraint that's easy to overlook in a purely technical build: a correct prediction that arrives too late is worthless. Retention campaigns take roughly 3–4 weeks to design and execute, so every prediction is paired with a reminder that action must be taken within 2–3 weeks of each monthly scoring cycle — otherwise the customer churns before the intervention ever reaches them.

All of this is delivered through an interactive **Streamlit dashboard** where users can browse the full subscriber base, drill into individual customers, override the recommended strategy, and simulate campaign ROI in real time.

### Tools Used

| Tool | Role |
|---|---|
| **Python** | Core language for the entire pipeline |
| **Pandas** | Data cleaning, feature engineering, EDA |
| **Scikit-learn** | Preprocessing, model training (Logistic Regression via GridSearchCV), evaluation |
| **Streamlit** | Interactive deployment — the churn & ROI dashboard |
| **GitHub** | Version control and project hosting |

---

## Project Status

**✅ Finished**

All phases of CRISP-DM are complete and documented:

| Phase | Status |
|---|---|
| Business Understanding | ✅ Complete — 5 Whys, KPIs, business levers, DS validation |
| Data Understanding | ✅ Complete — dictionary, samples |
| Exploratory Data Analysis | ✅ Complete — cleaning, feature engineering, preparation |
| Modeling | ✅ Complete — Logisitc Regression, Grid Search, 0 data leakage |
| Evaluation | ✅ Complete — Recall: 97%, F1-Score: 95%, AUC: 99% |
| Deployment | ✅ Complete — ROI Dashboard, Easy access |

---

## Funcionalities

The dashboard is built for the people who will actually use it day to day — retention managers, marketing leads, and finance analysts — not just data scientists. No coding or modeling knowledge is required to read any of the screens below.

### Portfolio Overview

A birds-eye view of the entire subscriber base, meant to answer *"how bad is the situation right now?"* in under a minute.

- **Subscriber Risk Distribution** — a donut chart showing what share of your subscribers fall into each risk tier (High, Medium, Low). The center number is your total subscriber count at a glance.
- **Avg. Churn Probability by Contract** — a bar chart comparing average churn risk across contract types. This usually makes the biggest lever obvious immediately: month-to-month subscribers are almost always the riskiest group, and this chart shows exactly by how much.
- **Churn Probability Distribution** — a histogram of every subscriber's individual risk score, with dashed lines marking where "Medium" and "High" risk begin. It shows how many subscribers are sitting just below a threshold — often the best return-on-effort group to act on first.

All charts are interactive: hover over any bar or slice to see exact numbers and subscriber counts.

### At-Risk Customers

A searchable, filterable list of every subscriber the model has scored, meant for day-to-day operational use.

- Click into any individual subscriber to see their full profile: churn probability, engagement signals (days since last login, support tickets, payment delays, data usage), and financial details (Customer Lifetime Value, tenure, monthly charges).
- Each subscriber comes with a **recommended retention action** already selected for you, along with its expected cost and expected revenue saved — no guesswork required.

### ROI Simulator

Turns the model's predictions into a business case, answering *"is this campaign worth running, and what will it cost?"*

- Four headline numbers: **Revenue at Risk** (how much revenue is exposed across at-risk subscribers), **Gross Revenue Saved** (expected recovery if the campaign runs), **Intervention Cost** (what the campaign will cost to execute), and **Net Projected Savings** (the bottom line).
- A **Campaign ROI Breakdown** chart showing how those four numbers relate to each other visually.
- A **Net Savings by Strategy** chart ranking each retention action by how much value it's expected to generate — useful for deciding where to focus budget first.
- A detailed **Strategy Breakdown table** with subscriber counts, average CLV, revenue saved, campaign cost, and net savings per retention action.

### Retention Actions

The simulator recommends one of seven retention actions for each at-risk subscriber, chosen automatically based on their risk level, plan tier, and value to the business:

| Action | When it's used |
|---|---|
| **Proactive Retention Call** | High-risk, high-value subscribers — a trained specialist reaches out directly |
| **Targeted Discount** | High-risk, more price-sensitive subscribers |
| **Service Upgrade** | Medium-risk Premium subscribers — a free upgrade or add-on |
| **Contract Lock-In Incentive** | Medium-risk subscribers on flexible, month-to-month plans |
| **Loyalty Program Enrollment** | Long-tenure subscribers showing early warning signs |
| **Personalized Re-engagement** | Lower-risk subscribers — a lightweight nudge campaign |
| **Priority Technical Support** | Subscribers churning due to unresolved service issues |

Each action carries its own estimated cost and expected success rate behind the scenes, which is what powers the ROI numbers above. You're never required to follow the recommendation — it's a starting point, not a rule.

### Bringing Your Own Data

The simulator is built to work with any subscriber dataset that follows the same structure, so you can plug in your own file instead of the sample data. Your file should be a **CSV** with one row per subscriber and include the following columns:

| Column | What it should contain |
|---|---|
| `customer_id` | A unique ID for each subscriber |
| `tenure_months` | How long the subscriber has had an active account, in months |
| `monthly_charges` | Their current monthly bill |
| `contract_type` | `Month-to-month`, `One-year`, or `Two-year` |
| `plan_type` | `Basic`, `Standard`, or `Premium` |
| `payment_method` | How the subscriber pays (e.g., Credit card, Bank transfer) |
| `payment_delay_days` | Average days late on payments over the last 6 months |
| `data_usage_gb` | Average monthly data usage in gigabytes |
| `has_streaming_addon` | `1` if they have the streaming bundle, `0` if not |
| `num_support_tickets` | Support tickets opened in the last 90 days |
| `last_login_days_ago` | Days since they last used the app or platform |
| `clv_estimated` | Their estimated Customer Lifetime Value |
| `churned` *(optional)* | `1` if the subscriber has already left, `0` if active |

**A few things worth knowing before you upload:**

- If your file includes a `churned` column, any subscriber marked as `1` is automatically excluded before scoring — the simulator only predicts churn for subscribers who are still active. You'll see a message telling you how many rows were removed this way.
- Subscribers with less than **3 months of tenure** are flagged separately as *New Subscribers* rather than scored for churn. Very new accounts naturally look "at risk" simply because they haven't built up usage history yet, so treating them as a churn case would be misleading — they're better suited to an onboarding campaign than a retention one.
- The more complete and recent your data is, the more reliable the risk scores will be. Missing values in key columns (especially `last_login_days_ago`, `payment_delay_days`, and `num_support_tickets`) will reduce the model's confidence for that subscriber.

### Business documentation
+ One gif page functionality
+ CRISP-DM notebook with EDA and modeling

---

## Access

### Non-technical users

The app can be opened directly in any modern browser — no installation required.

[Here is the page](https://churn-retention-leandro-diaz.streamlit.app/)

---

### Technical users

#### Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/LeandroD-240/churn_retention.git
cd churn_retention

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run main.py

# 4. Explore the rest of the files
# There are some interesting files
# The notebook, the dataset, the champion model
```

#### Project structure

```
├──churn_retention
│   └── data/
|       ├── champion.pkl                          # Champion model trained during experimentation
|       └── voxtel_data.csv                       # Dataset
│   └── notebook/
|       ├── Business_Context.md                   # Markdown file explaining the context of the company and the problem
|       ├── Data_dictionary.md                    # Explanation of the dataset and the valid data used on this project
|       ├── churn_and_retention_notebook.ipynb    # Notebook with the experimentation and charts made
|       └── Notebook files                        # Additional files related with the notebook
|   ├── img                                       # Logo for the page
|   ├── README.md                                 # This file
|   ├── main.py                                   # Python file to load and deploy the app page with the model and data
│   └── requirements.txt                          # Packages for pip
```

---

## Tecnologies

A

---

## License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.
