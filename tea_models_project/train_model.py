# RandomForest/train_model.py
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.ensemble import ExtraTreesClassifier

# Load dataset (using relative path)
data = pd.read_csv("tea_aroma_balanced.csv")

X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

# Encode labels
encoder = LabelEncoder()
y_enc = encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# Train model
model = ExtraTreesClassifier(random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Evaluate
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")
report = classification_report(y_test, y_pred, target_names=encoder.classes_)

print(f"Accuracy: {acc:.4f}")
print(f"F1-Score: {f1:.4f}")
print(report)

# Save model (relative path, same directory)
with open("ExtraTrees_model.pkl", "wb") as file:
    pickle.dump(model, file)

# Save report (relative path, same directory)
with open("ExtraTrees_report.txt", "w") as f:
    f.write(f"Accuracy: {acc:.4f}\nF1-Score: {f1:.4f}\n\n")
    f.write(report)

# Save confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=encoder.classes_, yticklabels=encoder.classes_)
plt.title("Confusion Matrix - Extra Trees")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()
plt.savefig("ExtraTrees_cm.png")
plt.close()

print("\n Extra Trees model trained and saved successfully!")
