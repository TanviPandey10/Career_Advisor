from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
from flask_cors import CORS

# ==============================================================
# Initialize Flask app and enable CORS
# ==============================================================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==============================================================
# Load all models and encoders
# ==============================================================
model_dir = os.path.join(os.getcwd(), "model")
print(f"📂 Loading models from: {model_dir}")

career_model_dict = joblib.load(os.path.join(model_dir, 'career_model.pkl'))
label_encoder_dict = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))

career_labels = [
    'career_engineer', 'career_artist', 'career_teacher', 'career_scientist',
    'career_writer', 'career_entrepreneur', 'career_lawyer', 'career_doctor',
    'career_designer', 'career_marketer', 'career_journalist', 'career_psychologist',
    'career_photographer', 'career_developer', 'career_researcher'
]

# ==============================================================
# Helper: preprocess user input
# ==============================================================
def preprocess_input(data):
    df = pd.DataFrame([data])

    # ✅ Ensure these columns exist
    for col in ['skills', 'interests', 'preferred_subjects', 'extracurriculars']:
        if col not in df.columns:
            df[col] = ''
        else:
            df[col] = df[col].astype(str)  # ensure string type to allow .str.contains()

    # ✅ Handle gender safely
    if 'gender' in df.columns:
        df['gender'] = df['gender'].replace({'Male': 1, 'Female': 0}).astype(int)
    else:
        df['gender'] = 0

    # ✅ Safe .str.contains() operations
    df['is_tech_skilled'] = df['skills'].str.contains('Python|Java|C\\+\\+|HTML|CSS', case=False, na=False).astype(int)
    df['is_data_science'] = df['skills'].str.contains('Machine Learning|Statistics', case=False, na=False).astype(int)
    df['is_finance_oriented'] = df['interests'].str.contains('Finance|Economics', case=False, na=False).astype(int)
    df['is_medical'] = df['preferred_subjects'].str.contains('Biology|Psychology', case=False, na=False).astype(int)
    df['is_law'] = df['preferred_subjects'].str.contains('Political Science|History|English', case=False, na=False).astype(int)
    df['is_creative'] = df['skills'].str.contains('Photoshop|Creativity|Sketching|CAD|Sewing', case=False, na=False).astype(int)
    df['is_communication'] = df['skills'].str.contains('Writing|Communication|Public Speaking|Voice Modulation', case=False, na=False).astype(int)
    df['is_artistic'] = df['skills'].str.contains('Singing|Instrument|Rhythm|Acting|Photography|Sewing|Dancing', case=False, na=False).astype(int)
    df['is_journalist'] = df['extracurriculars'].str.contains('Newspaper|Media Club', case=False, na=False).astype(int)
    df['is_psychologist'] = df['extracurriculars'].str.contains('Psych Club|Peer Counseling', case=False, na=False).astype(int)
    df['is_photographer'] = df['extracurriculars'].str.contains('Photography Club|Photo Walk', case=False, na=False).astype(int)
    df['is_developer'] = df['skills'].str.contains('Python|Java|C\\+\\+', case=False, na=False).astype(int)
    df['is_researcher'] = df['skills'].str.contains('Machine Learning|Statistics', case=False, na=False).astype(int)

    # ✅ Encode categorical columns safely
    for col in ['preferred_subjects', 'interests', 'extracurriculars']:
        if col in df.columns:
            le = label_encoder_dict.get(col)
            if le is not None:
                try:
                    df[col] = le.transform(df[col])
                except Exception:
                    df[col] = 0
            else:
                df[col] = 0
        else:
            df[col] = 0

    # ✅ Define required features
    features = [
        'gender', 'age', 'class_10_marks', 'class_12_marks',
        'preferred_subjects', 'interests', 'extracurriculars',
        'is_tech_skilled', 'is_data_science', 'is_finance_oriented',
        'is_medical', 'is_law', 'is_creative', 'is_communication',
        'is_artistic', 'is_journalist', 'is_psychologist', 'is_photographer',
        'is_developer', 'is_researcher'
    ]

    for col in features:
        if col not in df.columns:
            df[col] = 0

    return df[features]

# ==============================================================
# Routes
# ==============================================================

@app.route("/")
def home():
    return jsonify({"message": "Career prediction API is running 🚀"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("📩 Received data:", data)

        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        X = preprocess_input(data)
        results = {}

        for career, model in career_model_dict.items():
            y_proba = model.predict_proba(X)[:, 1][0]
            results[career] = round(y_proba * 100, 2)

        print("✅ Prediction complete.")
        return jsonify({
            "career_scores": results,
            "message": "Scores represent suitability out of 100 for each career"
        })

    except Exception as e:
        print("❌ Error during prediction:", e)
        return jsonify({"error": str(e)}), 500

# ==============================================================
# Run Flask app
# ==============================================================
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)






