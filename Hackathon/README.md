AI Transaction Categorizer
A Hybrid Rule-Based + Machine Learning System for Automated Transaction Classification
📌 Overview
The AI Transaction Categorizer is a fully local, privacy-preserving machine learning system that classifies financial transactions using a hybrid approach:
•	Rule-based classification using a YAML-driven keyword engine
•	Machine Learning classification using TF-IDF + Logistic Regression + Random Forest
•	Explainable AI (LIME) for transparency
•	Streamlit UI for interactive exploration
The system requires no external APIs and ensures all data stays completely on your machine.

📂 Project Structure
AI-Transaction-Categorizer/
│
├── app.py                     # Streamlit UI
├── predict.py                 # Prediction engine + LIME explainability
├── train.py                   # Training pipeline (TF-IDF + ML Ensemble)
├── setup.sh                   # Automated setup + training script
├── requirements.txt           # Project dependencies
│
├── data/                      # Synthetic training data
├── models/                    # model.pkl, vectorizer.pkl, categories.pkl
├── config/                    # taxonomy.yaml (rule-based classifier)
└── outputs/                   # metrics.json, confusion_matrix.png

🚀 Features

1. 🔍 Hybrid Classification Engine
•	TF-IDF vectorization
•	Logistic Regression + Random Forest soft-voting ensemble
•	YAML keyword rule engine for deterministic matches
•	Automatic fallback to ML for unknown merchants

2. 🧠 Explainable AI
•	Integrated LIME Text Explainer
•	Displays token-level influence for each prediction

3. 🖥 Interactive Web App
Powered by Streamlit:
•	Single transaction prediction
•	Batch CSV prediction
•	Editable taxonomy (YAML-based)
•	Metrics dashboard (confusion matrix, category distribution)

4. 🔐 Privacy & Security
•	100% offline
•	No cloud calls
•	Zero data exfiltration
•	GDPR-friendly

5. 🛠 Installation

a. Clone the repository
git clone https://github.com/Thor-asgardian/AI-Transaction-Categorizer
cd AI-Transaction-Categorizer
b. Run the automated setup
bash setup.sh
This will:
•	Create a virtual environment
•	Install all dependencies
•	Train the model
•	Generate taxonomy.yaml
•	Create data/models/config/outputs folders
c. ▶️ Running the App
streamlit run app.py
Visit:
http://localhost:8501

d. 🧪 Command-Line Predictions
Single prediction
python predict.py
Outputs:
•	Predicted category
•	Confidence score
•	Probabilities
•	Rule or ML method used
•	LIME explanation (top contributing words)
e. 📄 Taxonomy Rules (YAML)
Rules are located in:
config/taxonomy.yaml
Example block:
- name: Coffee/Dining
  threshold: 0.7
  keywords:
    - starbucks
    - cafe
    - espresso
  description: Restaurants, beverages, and dining.
📈 Model Outputs
Generated after training:
outputs/
•	metrics.json – F1 scores, accuracy, sample counts
•	confusion_matrix.png – category-level confusion matrix
models/
•	model.pkl – soft-voting ensemble
•	vectorizer.pkl – TF-IDF model
•	categories.pkl – class label list

5. 📦 Tech Stack
Core: Python 3.13
ML: scikit-learn, numpy, pandas
Explainability: LIME
UI: Streamlit
Config: PyYAML
Plots: Plotly, Matplotlib, Seaborn

6. 📚 Use Cases
•	FinTech apps
•	Automated bookkeeping
•	Personal finance tools
•	SME accounting software
•	Bank transaction insights

7. 👨💻 Author
Bhuvan R
GitHub: https://github.com/Thor-asgardian

