import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


def train_model():

    print("Loading feature dataset...")
    df = pd.read_csv("data/processed/features.csv")

    FEATURES = [
        "rrc_fail",
        "ho_fail",
        "packet_loss",
        "latency",
        "bgp_down",
        "if_down"
    ]

    X = df[FEATURES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training model...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        class_weight="balanced",  # ✅ important
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Evaluating model...\n")

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    os.makedirs("models", exist_ok=True)  # ✅ create folder if not exists
    joblib.dump(model, "src/models/rf_model.pkl")

    print("✅ Model saved at models/rf_model.pkl")


if __name__ == "__main__":
    train_model()