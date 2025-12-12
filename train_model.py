import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def add_rolling_features(df):
    df = df.copy()
    df["duty_hours"] = (df["duty_end"] - df["duty_start"]).dt.total_seconds()/3600.0

    df = df.sort_values(["crew_id","date"])
    df["hours_last_7_days"] = (
        df.groupby("crew_id")["duty_hours"].rolling(window=7, min_periods=1).sum().reset_index(level=0, drop=True)
    )

    df["num_nights_last_7_days"] = (
        df.groupby("crew_id")["is_night_duty"].rolling(window=7, min_periods=1).sum().reset_index(level=0, drop=True)
    )

    
    df["num_early_last_7_days"] = (
        df.groupby("crew_id")["is_early_start"].rolling(window=7, min_periods=1).sum().reset_index(level=0, drop=True)
    )

    df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek

    return df

def rule_based_fatigue_label(row):
    score = 0

    if row["duty_hours"]>9:
        score +=2
    
    elif row["duty_hours"] > 8:
        score += 1

    if row["rest_hours_before"]<10:
        score += 3

    elif row["rest_hours_before"] <12:
        score +=2

    if row["num_nights_last_7_days"] >= 3:
        score += 2

    elif row["num_early_last_7_days"] >= 3:
        score += 2

    if row["consecutive_work_days"] >= 6:
        score += 2

    elif row["consecutive_work_days"] >= 4:
        score += 1

    if row["hours_last_7_days"] >= 55:
        score += 3

    elif row["hours_last_7_days"] >= 45:
        score += 2

    if score <= 2:
        return 0
    elif score <= 5:
        return 1
    else:
        return 2

if __name__ == "__main__":
    df = pd.read_csv("data/roster_synthetic.csv", parse_dates=["duty_start","duty_end"])
    df = add_rolling_features(df)

    df["fatigue_label"] = df.apply(rule_based_fatigue_label, axis = 1)

    feature_cols =[
        "duty_hours",
        "rest_hours_before",
        "num_sectors",
        "is_night_duty",
        "is_early_start",
        "hours_last_7_days",
        "num_nights_last_7_days",
        "num_early_last_7_days",
        "consecutive_work_days",
        "day_of_week",

    ]

    x = df[feature_cols]
    y = df["fatigue_label"]

    x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight= "balanced"
    )
    model.fit(x_train, y_train)

    print("Train score:", model.score(x_train, y_train))
    print("Test score:", model.score(x_test, y_test))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/fatigue_model.pkl")
    joblib.dump(feature_cols, "models/feature_cols.pkl")

    print("Model saved to models/fatigue_model.pkl")