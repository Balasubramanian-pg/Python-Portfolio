import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# 1. SYNTHETIC DATA GENERATION
# We're building controlled missingness so you can see how 
# each mechanism actually behaves in practice. Real data 
# rarely labels its missingness, so learning to spot patterns 
# starts with understanding the ground truth.
# ---------------------------------------------------------
np.random.seed(42)
n = 1000
df = pd.DataFrame({
    "age": np.random.normal(40, 10, n),
    "income": np.random.normal(55000, 15000, n),
    "satisfaction": np.random.normal(7, 2, n)
})

# MCAR: completely random drop. No relationship to anything.
mcar_idx = np.random.choice(df.index, size=100, replace=False)
df.loc[mcar_idx, "age"] = np.nan

# MAR: missingness depends on OBSERVED data.
# Older people are less likely to report income. 
# We model this with a logistic curve tied to age.
p_missing_mar = 1 / (1 + np.exp(-(df["age"] - 45) / 5))
mar_mask = np.random.binomial(1, p_missing_mar) == 1
df.loc[mar_mask, "income"] = np.nan

# MNAR: missingness depends on the UNOBSERVED value itself.
# People with low satisfaction skip the survey. 
# We can't directly use NaN to set the mask, so we use the true values.
true_sat = df["satisfaction"].copy()
df.loc[true_sat < 5, "satisfaction"] = np.nan

# ---------------------------------------------------------
# 2. EDA: VISUALIZING MISSINGNESS PATTERNS
# First principle: missingness is a variable itself. 
# Treat it like one. A heatmap shows you if missingness 
# clusters together or spreads out.
# ---------------------------------------------------------
plt.figure(figsize=(8, 4))
sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap="viridis")
plt.title("Missing Data Pattern (White = Missing)")
plt.ylabel("Rows (sorted for visual clarity)")
plt.tight_layout()
plt.show()

# Quick stats: how much are we missing per column?
print(df.isnull().mean() * 100)

# ---------------------------------------------------------
# 3. TESTING FOR MCAR vs MAR
# You can't statistically prove MCAR, but you can test for 
# deviations from it. The logic: if missingness is truly random,
# the observed vs missing groups should look identical on 
# every OTHER variable.
# We'll run t-tests between groups for continuous variables.
# ---------------------------------------------------------
def check_mcar_proxy(df, target_col, test_cols):
    """
    Simple MCAR sanity check: compare means of other variables
    between rows where target_col is present vs missing.
    If p < 0.05 consistently, MCAR is unlikely.
    """
    present = df[df[target_col].notna()]
    missing = df[df[target_col].isna()]
    
    print(f"\n--- Testing if {target_col} is MCAR ---")
    for col in test_cols:
        if df[col].isnull().any(): 
            continue  # skip if test column is also messy
        t_stat, p_val = stats.ttest_ind(present[col], missing[col], equal_var=False)
        print(f"{col:15} | t={t_stat:6.3f}, p={p_val:.4f} {'❌ Rejects MCAR' if p_val < 0.05 else '✅ Consistent with MCAR'}")

# Run checks
check_mcar_proxy(df, "age", ["income", "satisfaction"])
check_mcar_proxy(df, "income", ["age", "satisfaction"])
check_mcar_proxy(df, "satisfaction", ["age", "income"])

# ---------------------------------------------------------
# 4. DETECTING MAR SIGNALS
# MAR means missingness correlates with OBSERVED data.
# We convert missingness into a binary indicator and check 
# its relationship with other columns.
# ---------------------------------------------------------
df["income_missing"] = df["income"].isna().astype(int)
corr = df[["age", "satisfaction", "income_missing"]].corr()
print("\n--- Correlation: Missingness Indicators vs Observed ---")
print(corr.round(3))

# If 'income_missing' correlates with 'age', that's a MAR signal.
# You'd typically model this with logistic regression in practice,
# but correlation is enough for EDA-level detection.

# ---------------------------------------------------------
# 5. THE MNAR REALITY CHECK
# MNAR is fundamentally untestable from the dataset alone.
# Why? Because the missing values are gone. You're trying to 
# prove a relationship with data that doesn't exist.
# The only way to address MNAR is:
# 1. Domain knowledge (e.g., "high-income people hide income")
# 2. Sensitivity analysis (impute under different MNAR assumptions)
# 3. External data/validation sets
# ---------------------------------------------------------
print("\n--- MNAR Note ---")
print("MNAR leaves no statistical fingerprint in the observed data.")
print("If satisfaction is MNAR, mean(imputed) will systematically differ from true mean.")
print("Always run sensitivity checks if MNAR is plausible.")

# ---------------------------------------------------------
# 6. NEXT-STEP GUIDANCE (Don't just fill with .mean())
# - MCAR  → mean/median/KNN imputation is usually safe
# - MAR   → model-based imputation (MICE, regression, KNN) works well
# - MNAR  → standard imputation will bias results. Use pattern-mixture 
#           models, selection models, or treat missingness as a feature.
# ---------------------------------------------------------
