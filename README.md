# ✈️ Pilot Fatigue Prediction System

### *A Data-Driven Fatigue Awareness Tool for Aviation Crew*

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-ff4b4b)
![License](https://img.shields.io/badge/License-MIT-orange)
![Model](https://img.shields.io/badge/Model-RandomForest-lightgrey)


## 🌟 Overview

Fatigue is one of the most critical risk factors in aviation. This project introduces a **lightweight fatigue-risk prediction system** that estimates a pilot’s relative fatigue level based on short-term duty records and rolling workload.

The tool highlights patterns such as:

* Short rest
* Long duty durations
* Early-morning reportings
* Night duties
* High weekly cumulative hours
* Consecutive working days

## ✨ Key Features

* Interactive **Streamlit interface**
* **Day-wise expanders** for clean input
* Automatic **rest computation**
* **OFF day support**
* Card-style fatigue output
* Emoji-based fatigue levels (🟢 🟡 🔴)
* Rolling 7-day workload metrics
* HH:MM formatted hours
* Perfect for **portfolio, academic work, and demonstrations**

## 🧠 How the Model Works

### **Input Features**

* Duty start & end time
* Duty duration
* Rest before duty
* Early start flag
* Night duty flag
* Number of sectors
* Consecutive work days
* Rolling 7-day duty hours
* Rolling 7-day early starts
* Rolling 7-day night duties
* Day of week / Day name

### **Model Output**

* **Fatigue Level:** Low / Medium / High
* **Fatigue Score:** 0–100 scale
* **Explanation:** “short rest”, “high weekly hours”, “many early starts”, etc.

## 🚀 Installation & Usage

### **1. Clone the Repository**

```bash
git clone https://github.com/pratapmangalam/pilot-fatigue-prediction.git
cd pilot-fatigue-prediction
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Run the Streamlit App**

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
├── app.py                   
├── models/
│   ├── fatigue_model.pkl
│   └── feature_cols.pkl
├── data/
│   └── sample_roster.csv
├── README.md
└── requirements.txt
```

---

## 📄 White Paper Summary

This project demonstrates how **data science can support aviation safety** by identifying fatigue-intensive roster patterns using:

* Duty-time analytics
* Rolling cumulative workload
* Simplified machine learning
* Transparent, interpretable explanations

It serves as a practical fatigue-awareness tool and a strong **portfolio project** showcasing real-world feature engineering, modelling, and UI design.
---

## 🔮 Future Enhancements

* Time-zone shift fatigue modeling
* Real-world dataset integration
* Sleep–wake cycle estimation
* What-if roster simulation
* Multi-crew comparison
* Premium PDF reporting
* Integration with advanced biomathematical models


## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a PR.

## 📜 License

This project is released under the **MIT License**.

## 🛩️ Acknowledgments

Inspired by real-world discussions on crew fatigue, aviation safety, and recent flight disruptions related to pilot fatigue.
