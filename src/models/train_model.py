import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score


# ---------------- LOAD DATA ----------------
def load_data():
    df = pd.read_csv("data/processed/features.csv")
    X = df.drop(columns=["callId", "target"])
    y = df["target"]
    return X, y


# ---------------- TRAIN ----------------
def train_model():
    print("Loading dataset...")
    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # ---------------- RANDOM FOREST ----------------
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    # ---------------- XGBOOST ----------------
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=2,   # imbalance handling
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    print("\nTraining Random Forest...")
    rf.fit(X_train, y_train)

    print("Training XGBoost...")
    xgb.fit(X_train, y_train)

    # ✅ ADD THIS BLOCK HERE
    from sklearn.model_selection import cross_val_score

    print("\nRunning Cross Validation...")
    rf_cv = cross_val_score(rf, X, y, cv=5, scoring="roc_auc")
    xgb_cv = cross_val_score(xgb, X, y, cv=5, scoring="roc_auc")

    print("RF CV ROC-AUC:", rf_cv.mean())
    print("XGB CV ROC-AUC:", xgb_cv.mean())

    # ---------------- EVALUATION ----------------
    print("\n===== RANDOM FOREST =====")
    rf_pred = rf.predict(X_test)
    rf_prob = rf.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, rf_pred))
    print("ROC-AUC:", roc_auc_score(y_test, rf_prob))

    print("\n===== XGBOOST =====")
    xgb_pred = xgb.predict(X_test)
    xgb_prob = xgb.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, xgb_pred))
    print("ROC-AUC:", roc_auc_score(y_test, xgb_prob))
    
    # ✅ ADD THIS BLOCK HERE
    import pandas as pd

    print("\nFeature Importance (Random Forest):")
    feat_imp = pd.Series(rf.feature_importances_, index=X.columns)
    print(feat_imp.sort_values(ascending=False))
    feat_imp.sort_values(ascending=False).to_csv("models/feature_importance.csv")

    # ✅ ADD THIS BLOCK HERE
    from sklearn.model_selection import cross_val_score

    print("\nRunning Cross Validation...")
    rf_cv = cross_val_score(rf, X, y, cv=5, scoring="roc_auc")
    xgb_cv = cross_val_score(xgb, X, y, cv=5, scoring="roc_auc")

    print("RF CV ROC-AUC:", rf_cv.mean())
    print("XGB CV ROC-AUC:", xgb_cv.mean())

    

    # ---------------- SAVE ----------------
    joblib.dump(rf, "models/rf_model.pkl")
    joblib.dump(xgb, "models/xgb_model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")

    print("\n✅ Both models saved!")

    return rf, xgb, scaler


if __name__ == "__main__":
    train_model()