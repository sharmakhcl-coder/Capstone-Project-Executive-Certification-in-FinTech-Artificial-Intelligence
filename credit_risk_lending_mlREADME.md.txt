Part D — Bias-awareness note and final recommendation

Summary of the key findings from the model comparison and anomaly detection tasks:

Model Comparison (Credit Default Prediction):

Logistic Regression outperformed the Decision Tree Classifier in predicting credit defaults. It achieved a significantly higher ROC-AUC score of 0.72 (compared to 0.49 for Decision Tree) and better Recall of 0.35 (vs. 0.25).
The Logistic Regression model's predicted probabilities were used to create a risk-based pricing table with 4 tiers, demonstrating a clear monotonic relationship between predicted risk and observed default rates, which is crucial for fair and effective lending strategies.
Anomaly Detection (Transaction Behavior):

The Isolation Forest model, trained on standardized numeric transaction features, successfully identified 11 out of 15 injected anomalies, achieving a recall of 0.73.
This indicates that the Isolation Forest is effective in flagging unusual transaction patterns, which can be critical for fraud detection or identifying suspicious activities.
In essence, Logistic Regression is the stronger candidate for predicting credit default due to its higher discriminative power and better ability to identify actual defaulters, while Isolation Forest is a valuable tool for detecting anomalies in transactional data.