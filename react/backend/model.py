import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
import joblib
import os

# ============================================================== #
# 📥 Load dataset
# ============================================================== #
df = pd.read_csv('/content/students_dataset_2000_15careers.csv')

# Fill missing text fields
for col in ['skills', 'interests', 'preferred_subjects', 'extracurriculars']:
    df[col] = df[col].fillna('').astype(str)

# ============================================================== #
# 🧠 Feature Engineering
# ============================================================== #
df['is_tech_skilled'] = df['skills'].str.contains('Python|Java|C\\+\\+|HTML|CSS', case=False).astype(int)
df['is_data_science'] = df['skills'].str.contains('Machine Learning|Statistics', case=False).astype(int)
df['is_finance_oriented'] = df['interests'].str.contains('Finance|Economics', case=False).astype(int)
df['is_medical'] = df['preferred_subjects'].str.contains('Biology|Psychology', case=False).astype(int)
df['is_law'] = df['preferred_subjects'].str.contains('Political Science|History|English', case=False).astype(int)
df['is_creative'] = df['skills'].str.contains('Photoshop|Creativity|Sketching|CAD|Sewing', case=False).astype(int)
df['is_communication'] = df['skills'].str.contains('Writing|Communication|Public Speaking|Voice Modulation', case=False).astype(int)
df['is_artistic'] = df['skills'].str.contains('Singing|Instrument|Rhythm|Acting|Photography|Sewing|Dancing', case=False).astype(int)
df['is_journalist'] = df['extracurriculars'].str.contains('Newspaper|Media Club', case=False).astype(int)
df['is_psychologist'] = df['extracurriculars'].str.contains('Psych Club|Peer Counseling', case=False).astype(int)
df['is_photographer'] = df['extracurriculars'].str.contains('Photography Club|Photo Walk', case=False).astype(int)
df['is_developer'] = df['skills'].str.contains('Python|Java|C\\+\\+', case=False).astype(int)
df['is_researcher'] = df['skills'].str.contains('Machine Learning|Statistics', case=False).astype(int)

# ============================================================== #
# 🔤 Encode categorical features (store encoders properly)
# ============================================================== #
label_cols = ['gender', 'preferred_subjects', 'interests', 'extracurriculars']
label_encoder_dict = {}

for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoder_dict[col] = le

# ============================================================== #
# 🎯 Features and Targets
# ============================================================== #
X = df[[
    'gender', 'age', 'class_10_marks', 'class_12_marks',
    'preferred_subjects', 'interests', 'extracurriculars',
    'is_tech_skilled', 'is_data_science', 'is_finance_oriented',
    'is_medical', 'is_law', 'is_creative', 'is_communication',
    'is_artistic', 'is_journalist', 'is_psychologist', 'is_photographer',
    'is_developer', 'is_researcher'
]]

career_labels = [
    'career_engineer', 'career_artist', 'career_teacher', 'career_scientist',
    'career_writer', 'career_entrepreneur', 'career_lawyer', 'career_doctor',
    'career_designer', 'career_marketer', 'career_journalist', 'career_psychologist',
    'career_photographer', 'career_developer', 'career_researcher'
]

# ============================================================== #
# 💾 Prepare model directory
# ============================================================== #
model_dir = '/content/model'
os.makedirs(model_dir, exist_ok=True)

career_model_dict = {}

# ============================================================== #
# 🧩 Train individual models
# ============================================================== #
for career in career_labels:
    print(f"\n🚀 Training model for: {career}")
    y = df[career]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Handle imbalance using SMOTE
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    # Train model
    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=30,
        min_samples_split=2,
        class_weight='balanced',
        random_state=42
    )
    model.fit(X_resampled, y_resampled)

    # Evaluate
    y_proba = model.predict_proba(X_test)[:, 1]
    threshold = 0.4 if career in ['career_artist', 'career_writer', 'career_marketer'] else 0.5
    y_pred = (y_proba > threshold).astype(int)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"✅ {career:<20} | Acc: {acc:.2f} | Prec: {prec:.2f} | Rec: {rec:.2f} | F1: {f1:.2f}")

    # Save model
    model_path = os.path.join(model_dir, f'{career}_model.pkl')
    joblib.dump(model, model_path)
    career_model_dict[career] = model

# ============================================================== #
# 🧳 Save combined models & encoders
# ============================================================== #
joblib.dump(career_model_dict, os.path.join(model_dir, 'career_model.pkl'))
print("📦 Saved unified career_model.pkl")

joblib.dump(label_encoder_dict, os.path.join(model_dir, 'label_encoder.pkl'))
print("📦 Saved label_encoder.pkl")

print("\n🎯 All career models trained, evaluated, and saved successfully.")

 
 