# 🚀 SkillMatch – Resume Matcher & Skill Recommender

SkillMatch is an AI-powered Resume Matcher and Skill Recommender that analyzes resumes against job descriptions, calculates similarity scores, and suggests missing skills using NLP techniques.

---

## 🚀 Features

* Resume text analysis
* Job description keyword extraction
* Similarity score calculation
* Skill gap identification
* Intelligent skill recommendations
* Simple and interactive interface using Streamlit

---

## 🛠️ Technologies Used

* Python
* Streamlit
* NLP (Natural Language Processing)
* Scikit-learn
* PDFPlumber (for resume parsing)
* SQLite (for user data storage)

---

## 📂 Project Structure

SkillMatch/
│── app.py
│── resume.txt
│── job_description.txt
│── requirements.txt
│── README.md

---

## ⚙️ How It Works

1. The system reads the resume and job description
2. Text is preprocessed (lowercase conversion, special character removal)
3. Important keywords/skills are extracted using NLP
4. Similarity score is calculated using TF-IDF and Cosine Similarity
5. Missing skills are identified
6. Skill recommendations are provided

---

## ▶️ How to Run the Project

1. Clone the repository
   git clone https://github.com/AgumamidiJahnavi5/SkillMatch---Resume-Matcher-and-Skill-Recommender

2. Navigate to the project folder
   cd SkillMatch

3. Install dependencies
   pip install -r requirements.txt

4. Run the application
   streamlit run app.py

---

## 📊 Output

* Match Score Percentage
* Extracted Resume Skills
* Extracted Job Skills
* Matching Skills
* Missing Skills
* Suggested Skills

---

## 🎯 Future Improvements

* Advanced NLP using Transformers (BERT / SBERT)
* Resume PDF upload enhancement
* Multiple job comparison
* Improved UI/UX design
* Cloud deployment (Streamlit Cloud / AWS)

---

## 🙌 Conclusion

SkillMatch simplifies resume screening by automating skill comparison and recommendation, helping both recruiters and job seekers make better decisions.




