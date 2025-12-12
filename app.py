import streamlit as st
import pandas as pd
import joblib
from datetime import datetime, time, date, timedelta
import io

st.set_page_config(page_title= "Aviation Fatigue Predictor", page_icon='✈️', layout='wide')
st.title("Aviation Crew Fatigue Prediction")
st.caption("Enter a short stretch of duties (with OFF days). The app estimates relative fatigue risk per day.")

st.markdown("""
<style>
div.stCheckbox > label { line-height: 1.05rem; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data

def load_model():
    model = joblib.load("models/fatigue_model.pkl")
    feature_cols = joblib.load("models/feature_cols.pkl")
    return model, feature_cols

def explain_reason(row):
    reasons = []
    if row.get("rest_hours_before", 999) < 10:
        reasons.append("Short rest")
    if row.get("num_early_last_7_days", 0) >= 3:
        reasons.append("Many early starts (7d)")
    if row.get("num_nights_last_7_days", 0) >= 3:
        reasons.append("Many night duties (7d)")
    if row.get("hours_last_7_days", 0) > 55:
        reasons.append("High weekly hours")
    if row.get("is_night_duty", 0) == 1:
        reasons.append("Night duty")
    if row.get("duty_hours", 0) >= 10:
        reasons.append("Long duty")
    return " + ".join(reasons) if reasons else "Normal pattern"

def predict_fatigue(df_features, model, feature_cols):
        for c in feature_cols:
            if c not in df_features.columns:
                df_features[c] = 0
        x = df_features[feature_cols]
        probs = model.predict_proba(x)
        preds = model.predict(x)
        high_idx = list(model.classes_).index(2)
        high_prob = probs[:, high_idx]
        score = (high_prob * 100).round(1)
        level_map = {0: "Low", 1: "Medium", 2: "High"}
        out = df_features.copy()
        out["fatigue_score"] = score
        out["fatigue_level"] = [level_map[p] for p in preds]
        out["reason"] = out.apply(explain_reason, axis=1)
        return out

def hours_to_hhmm(h):
    try:
        if pd.isna(h):
            return""
    except Exception:
        pass
    total_minutes = int(round(float(h)*60))
    hours = total_minutes //60
    minutes = total_minutes%60
    return f"{hours:d}:{minutes:02d}"

model, feature_cols = load_model()


today = datetime.today().date()
rows = []

st.markdown("### Roster Input")
colA, colB = st.columns(2)
with colA:
    num_days = st.number_input("Number of days to enter",1,31,7)
with colB:
    initial_rest_hours = st.number_input("Rest hours before Day1", 0,200,12,1)

prev_duty_end = None
consec_counter = 0

for i in range(num_days):
    with st.expander(f"Day {i+1}", expanded=(i == 0)):
        c1,c2 = st.columns([2,2])

        with c1:
            date = st.date_input("Date", today + timedelta(days=i), key=f"date_{i}")
            is_off = st.checkbox("OFF / Rest day", False, key=f"off_{i}")
            
            if not is_off: 
                is_early = st.checkbox("Early start", False, key=f"early_{i}")
                is_night = st.checkbox("Night duty", False, key=f"night_{i}")
            else: 
                is_early = False
                is_night = False
  
        with c2:
            if not is_off:
                start_time = st.time_input("Duty start 🛫 ",datetime(2025, 1, 1, 6, 0).time(),key=f"start_{i}" )
                end_time = st.time_input("Duty end 🛬",datetime(2025, 1, 1, 14, 0).time(),key=f"end_{i}")
                num_sectors = st.number_input("Sectors",min_value=1,max_value=4,value=2, key=f"sectors_{i}")
            else:
                start_time, end_time = None, None, 
                num_sectors = 0

        if is_off:
            consec_counter = 0
            rest_hours = max(initial_rest_hours, 24.0)
            rows.append({
                "crew_id": "MANUAL",
                "date": date,
                "duty_start": pd.NaT,
                "duty_end": pd.NaT,
                "num_sectors": num_sectors,
                "is_night_duty": 0,
                "is_early_start": 0,
                "rest_hours_before": rest_hours,
                "duty_hours": 0.0,
                "consecutive_work_days": 0
            })
            prev_duty_end = None
            continue

        duty_start = datetime.combine(date, start_time)
        duty_end = datetime.combine(date, end_time)
        duty_hours = (duty_end - duty_start).total_seconds() / 3600.0
        if duty_hours < 0:
            duty_hours += 24.0

        if prev_duty_end is None:
            rest_hours = initial_rest_hours
        else:
            rest_hours = (duty_start - prev_duty_end).total_seconds() / 3600.0

        consec_counter += 1
        prev_duty_end = duty_end

        rows.append({
            "crew_id": "MANUAL",
            "date": date,
            "duty_start": duty_start,
            "duty_end": duty_end,
            "num_sectors": int(num_sectors),
            "is_night_duty": int(is_night),
            "is_early_start": int(is_early),
            "rest_hours_before": rest_hours,
            "duty_hours": duty_hours,
            "consecutive_work_days": consec_counter
        })

if st.button("Predict fatigue"):
    if len(rows) == 0:
        st.warning("No days entered.")
    else:
        df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        df["hours_last_7_days"] = df["duty_hours"].rolling(window=7,min_periods=1).sum()
        df["num_nights_last_7_days"] = df["is_night_duty"].rolling(window=7,min_periods=1).sum()
        df["num_early_last_7_days"] = df["is_early_start"].rolling(window=7,min_periods=1).sum()
        df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
        df["day_name"] = pd.to_datetime(df["date"]).dt.day_name()

        df_out = predict_fatigue(df, model, feature_cols)
#summary
        n_high = (df_out["fatigue_level"] == "High").sum()
        n_med = (df_out["fatigue_level"] == "Medium").sum()
        n_low = (df_out["fatigue_level"] == "Low").sum()
        msg = f"Over these {len(df_out)} days: 🟢 Low: {n_low}, 🟡 Medium: {n_med}, 🔴 High: {n_high}."
        if n_high > 0:
            st.error(msg + " High fatigue detected; adjust schedules promptly. Wishing smoother rotations ahead! ✈️")
        elif n_med > 0:
            st.warning(msg + "Moderate fatigue: maintain balanced duties and monitor rest patterns. Stay sharp, stay rested! ✈️")
        else:
            st.success(msg + " Fatigue levels look minimal. Smooth flights ahead! ✈️")

        
        st.markdown("### Predictions")
        badge_color = {"Low": "#27ae60", "Medium": "#f1c40f", "High": "#e74c3c"}
        badge_map = {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}
        
        for _, r in df_out.iterrows():
            duty_hhmm = hours_to_hhmm(r["duty_hours"])
            rest_hhmm = hours_to_hhmm(r["rest_hours_before"])
            weekly_hhmm = hours_to_hhmm(r["hours_last_7_days"])
            badge_text = f"{badge_map[r['fatigue_level']]} — {r['fatigue_score']}%"
            color = badge_color[r["fatigue_level"]]
            
            card_html = f"""
                <div style="
                    padding:12px;
                    border:1px solid #444;
                    border-radius:10px;
                    margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <b>{str(r['date']).split(' ')[0]} ({r.get('day_name','')})</b>
                            — Duty hrs: {duty_hhmm}
                            • Rest before: {rest_hhmm}
                            • Week hrs: {weekly_hhmm}
                        </div>
                        <div style="
                            font-weight:bold; padding:6px 10px; border-radius:6px;
                            background-color:{color}; color:white;">
                            {badge_text}
                        </div>
                    </div>
                    <div style="margin-top:6px; opacity:0.85;">Reason: {r['reason']}</div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
 
        display = df_out.copy()
        display["duty_hours"] = display["duty_hours"].apply(hours_to_hhmm)
        display["rest_hours_before"] = display["rest_hours_before"].apply(hours_to_hhmm)
        display["hours_last_7_days"] = display["hours_last_7_days"].apply(hours_to_hhmm)

        display_cols = ["date", "day_name", "duty_hours", "rest_hours_before","hours_last_7_days","fatigue_score","fatigue_level","reason"]
        st.markdown("### Table view")
        st.dataframe(display[display_cols].rename(columns={"day_name":"Day"}), use_container_width=True)
        st.caption("Note: Prototype for awareness, not a medical or regulatory assessment.")

        st.markdown(
        "<p style='text-align: center;'> Happy Landings!!!✨✈️ </p>",
        unsafe_allow_html=True
        )