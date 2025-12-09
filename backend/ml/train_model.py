import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

np.random.seed(42)

# Generate synthetic dataset for underwriting
# Features: [income, loan_amount, tenure]
X = np.random.rand(1000, 3)
X[:, 0] *= 100000  # income
X[:, 1] *= 500000  # loan amount
X[:, 2] = (X[:, 2] * 60 + 6).astype(int)  # tenure 6-66 months

# Rule of thumb: approve if EMI < 40% of income
# EMI approximation: loan_amount / tenure
emi = X[:, 1] / X[:, 2]
y = (emi < 0.4 * X[:, 0]).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

joblib.dump(clf, "backend/ml/model.pkl")
print("Model saved to backend/ml/model.pkl")
