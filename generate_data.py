import numpy as np
import pandas as pd

np.random.seed(42)

def generate_synthetic_roster(num_crew=20, num_days=60):
    dates = pd.date_range("2025-01-01",periods=num_days,freq="D")
    records = []

    for crew_id in range(1, num_crew + 1):
        consecutive_work_days = 0
        prev_duty_end = None

        for d in dates:
            is_off = np.random.rand() < 0.23

            if is_off:
                consecutive_work_days = 0
                prev_duty_end = None
                continue

            consecutive_work_days +=1

            pattern = np.random.choice(["Early","Day","Late","Night"], p = [0.25,0.4,0.2,0.15])

            if pattern == "Early":
                start_hour = np.random.randint(4,7)
                duration_hours = np.random.uniform(6,10)

            elif pattern =="Day":
                start_hour = np.random.randint(8, 17)
                duration_hours = np.random.uniform(6,10)

            elif pattern =="Late":
                start_hour = np.random.randint(18,24)
                duration_hours = np.random.uniform(6,9)

            else: #pattern =="Night":
                start_hour = np.random.randint(0,3)
                duration_hours = np.random.uniform(6,8)
            
            start_minute = np.random.choice([0,15,30,45])
            duty_start = pd.Timestamp(d.year, d.month, d.day, start_hour, start_minute)
            duty_end = duty_start + pd.Timedelta(hours=duration_hours)

            is_night_duty = int((duty_end.hour < duty_start.hour) or pattern=="Night")
            num_sectors = np.random.randint(1,5)

            if prev_duty_end is None:
                rest_hours_before = np.random.randint(24,72)
            else: 
                rest_hours_before = (duty_start - prev_duty_end).total_seconds()/3600.0

            prev_duty_end = duty_end

            records.append({
                "crew_id": f"C{crew_id:03d}",
                "date": d.date(),
                "duty_start": duty_start,
                "duty_end": duty_end,
                "num_sectors" : num_sectors,
                "is_night_duty" : is_night_duty,
                "is_early_start" : int(duty_start.hour < 6),
                "duration_hours" : duration_hours,
                "rest_hours_before" : rest_hours_before,
                "consecutive_work_days" : consecutive_work_days
            })

    df = pd.DataFrame(records)

    df = df.sort_values(["crew_id","date"]).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_synthetic_roster()
    df.to_csv("data/roster_synthetic.csv", index=False)
    print(df.head())
    print("succesfully saved!!!")
    print("Saved to data/roster_synthetic.csv ")