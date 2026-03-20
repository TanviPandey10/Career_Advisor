 import React, { useState } from "react";
import "./CareerForm.css";

const CareerForm = () => {
  const [formData, setFormData] = useState({
    gender: "Female",
    age: 17,
    class_10_marks: 85,
    class_12_marks: 88,
    preferred_subjects: 3,
    extracurriculars: 2,
    is_tech_skilled: 0,
    is_data_science: 0,
    is_finance_oriented: 0,
    is_management: 0,
    is_communication: 1,
    is_artistic: 1,
    is_journalist: 0,
    is_psychologist: 1,
    is_photographer: 0,
    is_teacher: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        value === "true" ? true : value === "false" ? false : value, // handle boolean/number/text
    }));
  };

  // Submit to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong. Check your backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="career-form-container">
      <h2>🎓 Career Recommendation Form</h2>
      <form className="career-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Gender:</label>
          <select name="gender" value={formData.gender} onChange={handleChange}>
            <option>Female</option>
            <option>Male</option>
            <option>Other</option>
          </select>
        </div>

        <div className="form-group">
          <label>Age:</label>
          <input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Class 10 Marks:</label>
          <input
            type="number"
            name="class_10_marks"
            value={formData.class_10_marks}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Class 12 Marks:</label>
          <input
            type="number"
            name="class_12_marks"
            value={formData.class_12_marks}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Preferred Subjects (1–5):</label>
          <input
            type="number"
            name="preferred_subjects"
            value={formData.preferred_subjects}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Extracurriculars (1–5):</label>
          <input
            type="number"
            name="extracurriculars"
            value={formData.extracurriculars}
            onChange={handleChange}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Get Career Recommendations"}
        </button>
      </form>

      {result && (
        <div className="results">
          <h3>Career Suitability Scores:</h3>
          <ul>
            {Object.entries(result.career_scores)
              .sort((a, b) => b[1] - a[1])
              .map(([career, score]) => (
                <li key={career}>
                  <strong>{career.replace("career_", "")}</strong>:{" "}
                  {score.toFixed(1)}%
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CareerForm;
