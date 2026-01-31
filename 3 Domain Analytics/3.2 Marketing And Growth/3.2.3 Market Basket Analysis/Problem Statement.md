# Association Rule Learning – Market Basket Analysis using Apriori Algorithm

## 1. Problem Statement

When people go grocery shopping, they often follow a **recurring pattern** of buying specific items together.
These patterns vary by customer type — for example:

* A homemaker might buy **vegetables, cooking oil, and rice** for a family meal.
* A bachelor might opt for **instant noodles, chips, and beer**.

Identifying these **frequent combinations of items** can help businesses optimize sales in multiple ways:

1. **Shelf Arrangement**
   Frequently bought-together items can be placed closer to each other to prompt additional purchases.
2. **Targeted Promotions**
   Discounts can be applied to one item in a pair, increasing sales of both.
3. **Cross-Selling through Advertising**
   Ads for one product can be targeted at customers who often buy another related product.
4. **Product Bundling**
   Two or more items can be packaged together as a combo product.

While **intuition** might suggest some product pairings, **data analysis** allows us to **systematically uncover these associations** from historical sales records.

This concept extends beyond retail.
For example:

* **Healthcare:** Discovering which symptoms tend to occur together (co-morbidity).
* **Banking:** Identifying services often used by the same customers.
* **E-commerce:** Recommending products based on customers’ browsing and purchase history.

---

## 2. What is Association Rule Learning?

**Association Rule Learning** is a **rule-based machine learning method** for discovering relationships between variables in large datasets.
The most common example is **Market Basket Analysis**, where we analyze purchase records to find sets of items frequently bought together.

A typical association rule is written as:

```
{X, Y} → {Z}
```

This means that **if a customer buys X and Y, they are likely to also buy Z**.

Example:

```
{onions, chicken masala} → {chicken}
```

This indicates that customers who buy **onions** and **chicken masala** together have a high probability of also purchasing **chicken**.

---

## 3. Apriori Algorithm

The **Apriori Algorithm** (proposed in 1994 by Rakesh Agrawal and Ramakrishnan Srikant) is a foundational method for discovering **frequent itemsets** in a transactional database and generating **association rules**.

The term *Apriori* comes from the fact that the algorithm uses **prior knowledge of frequent itemsets** to find larger ones. It uses a bottom-up approach:

1. Start with single items.
2. Build larger itemsets step-by-step, keeping only those that meet a **minimum support threshold**.

---

## 4. Key Metrics in Association Rule Learning

Apriori measures the strength and usefulness of an association rule using three main metrics: **Support, Confidence, and Lift**.

### 4.1 Support

**Definition:**
The proportion of transactions that contain an itemset.

Formula:

```
Support(X) = (Number of transactions containing X) / (Total number of transactions)
```

Example:
If {apple} appears in **4 out of 8 transactions**,

```
Support({apple}) = 4/8 = 50%
```

Support tells us **how popular an item or itemset is**.

---

### 4.2 Confidence

**Definition:**
The proportion of transactions containing **X** that also contain **Y**.

Formula:

```
Confidence(X → Y) = Support(X ∪ Y) / Support(X)
```

Example:
If {apple, beer} appears in **3 out of 8 transactions**, and {apple} appears in **4 out of 8**,

```
Confidence({apple} → {beer}) = (3/8) / (4/8) = 75%
```

Confidence tells us **how often Y is purchased when X is purchased**.

**Drawback:** High confidence may occur simply because Y is popular, not because X and Y are truly related.

---

### 4.3 Lift

**Definition:**
Lift adjusts confidence to account for the popularity of Y.

Formula:

```
Lift(X → Y) = Confidence(X → Y) / Support(Y)
```

Example:
If Support({beer}) = 3/8,

```
Lift({apple} → {beer}) = 0.75 / (3/8) = 2.0
```

* **Lift > 1** → X and Y are positively correlated (buying X increases likelihood of buying Y).
* **Lift = 1** → X and Y are independent.
* **Lift < 1** → X and Y are negatively correlated.

---

## 5. How Apriori Works

### Step-by-step:

1. **Set minimum support and confidence thresholds.**
2. **Find all itemsets** that meet the minimum support.
3. **Generate rules** from these frequent itemsets that meet the minimum confidence.
4. **Rank rules** based on lift to find the most meaningful associations.

---

## 6. Applications Beyond Retail

* **Healthcare:** Symptom co-occurrence, drug side effects.
* **Fraud Detection:** Patterns in fraudulent transactions.
* **Web Usage Mining:** Pages often visited together.
* **Telecommunications:** Services purchased in bundles.

---

## 7. References

* Agrawal, R., & Srikant, R. (1994). *Fast algorithms for mining association rules*.
* Han, J., Kamber, M., & Pei, J. (2011). *Data Mining: Concepts and Techniques*.

---

If you want, I can extend this into a **full Jupyter Notebook** implementation of Apriori, complete with example datasets, visualizations of support-confidence-lift, and product recommendation outputs so it becomes a ready-to-run project. That would make it both theoretical and practical.
