# **🏋️ Sword ML Engineer Test**
> **Data Transformation and AI Message Generation Pipeline**

## **📌 Index**
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Branching Strategy](#branching-strategy)
4. [Setup Instructions](#setup-instructions)
5. [Data Transformation](#data-transformation)
6. [AI Message Generation](#ai-message-generation)
7. [Running the Pipeline](#running-the-pipeline)
8. [Testing](#testing)
9. [Future Improvements](#future-improvements)

---

## **📌 Project Overview**
This project automates **patient follow-up messaging** based on **session performance data** by leveraging:
- **Data Transformation:** Aggregating raw session data (`exercise_results.parquet`) into a structured format using **DuckDB & SQL**.
- **AI Message Generation:** Generating **personalized messages** for patients using **OpenAI GPT-4**.

The goal is to:
✔️ **Enable data-driven decision-making** for PTs  
✔️ **Ensure consistent & engaging** patient communication  
✔️ **Reduce manual workload** by automating messaging  

---

## **👤 Repository Structure**
```
ml-engineer-test/
│── message/                        # Core application logic
│   ├── data.py                     # Data transformation logic
│   ├── main.py                     # Entry point for commands (transform, get_message)
│   ├── model.py                    # OpenAI model integration
│   ├── prompt_manager.py           # Manages AI prompt templates
|   ├── config.py    
│── prompts/                        # AI message templates
│   ├── system_prompt.txt
│   ├── user_prompt.txt
│   ├── scenario_ok.txt
│   ├── scenario_nok.txt
│── data/                           # Raw & transformed datasets
│   ├── exercise_results.parquet    # Input
│   ├── features_expected.parquet   # Expected Output
│   ├── features.parquet            # Output
│── notebooks/                      # Jupyter Notebooks for debugging
│   ├── data-transformation.ipynb   # Testing for Question 1
│   ├── message-generation.ipynb    # Testing for Question 2
│── queries/                        # SQL queries for DuckDB
│── tests/                          # Unit tests for queries
│   ├── test_transformations.py 
│── Makefile                        # Command-line automation
│── requirements.txt                # Dependencies
│── README.md                       # Project documentation
```

---

## **🌱 Branching Strategy**
This project follows a **feature-branch workflow**:

| Branch                          | Purpose                                   |
|---------------------------------|-------------------------------------------|
| **main**                        | Stable production-ready code              |
| **feature/data-transformation** | Question 1                                |
| **feature/ai-generated-message**| Question 2                                |
| **Documentation**               | Organizing Readme                         |

Merging was done via **separate PRs per feature branch** to keep changes modular and reviewable, and to simmulate real productization scenario.

---

## **⚙️ Setup Instructions**
### **1️⃣ Clone the repository**
```bash
git clone <your-repo-url>
cd ml-engineer-test
```

### **2️⃣ Create & Activate Virtual Environment**
```bash
make venv  # Automatically creates and activates a virtual environment
source venv/bin/activate 
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Setup Environment Variables**
Create a `.env` file in the project root:
```bash
touch .env
```
Add your **OpenAI API Key** inside `.env`:
```
OPENAI_API_KEY=your-openai-key-here
```

---

## **🏋️ Data Transformation Summary**

### **💡 Key Objectives**
✔️ **Convert raw exercise records into structured session-level features**  
✔️ **Compute essential performance metrics** (e.g., `perc_correct_repeats`, `training_time`, `quality_rating`)  
✔️ **Identify skipped exercises & the most incorrect movements**  
✔️ **Validate alignment with `features_expected.parquet`**  

---

## **🛠️ Transformation Pipeline**

### **📌 Step 1: Session-Level Aggregation**
Each row in `exercise_results` represents **one exercise performed in a session**. To transform it into **one row per session**, we:

- **Group by `session_group`**
- Use **`ANY_VALUE()`** for static session-wide attributes:
  - `patient_id`, `therapy_name`, `session_number`, `pain`, `fatigue`, `quality`

### **📌 Step 2: Compute Performance Metrics**
- **Total prescribed repetitions:** `SUM(prescribed_repeats)`
- **Total training time:** `SUM(training_time)`
- **% Correct Repeats:**
  ```sql
  (SUM(correct_repeats) / NULLIF(SUM(correct_repeats + wrong_repeats), 0)) AS perc_correct_repeats
  ```
- **Number of exercises performed:** `COUNT(*)`
- **Distinct exercises performed:** `COUNT(DISTINCT exercise_name)`

### **📌 Step 3: Identify Key Exercises**
- **Exercise with most incorrect movements:**
  - Uses `ROW_NUMBER()` to **select the exercise with the highest mistakes**
  - Uses `RANDOM()` for **tie-breaking**
- **First skipped exercise:**
  - Uses `ORDER BY exercise_order ASC` to **identify the first skipped exercise**.

### **📌 Step 4: Count `leave_exercise` Reasons**
- Counts occurrences of `leave_exercise` for each session:
  ```sql
  COUNT(CASE WHEN leave_exercise = 'pain' THEN 1 END) AS leave_exercise_pain
  COUNT(CASE WHEN leave_exercise = 'technical_issues' THEN 1 END) AS leave_exercise_technical_issues
  ```

---

### **📝 SQL Transformation**
Stored in **`queries/features.sql`**, executed via **DuckDB**.


### **🛠 Python Execution**
The transformation is executed in **`transform_features_sql()`**:

```python
@app.command()
def transform():
    exercise_df = pd.read_parquet(Path(DATA_DIR, "exercise_results.parquet"))
    transform_features_sql(tables_to_register=[("exercise_results", exercise_df)])
```

---

### **🔍 Validation & Testing**
To ensure correctness, we:
✔ **Compare `features.parquet` vs `features_expected.parquet` using Pandas**  
✔ **Validate key aggregations using unit tests (`pytest`)**  


### **📊 Jupyter Notebook Comparisons**
We **compared outputs** for correctness, being all columns matching apart from `exercise_with_most_incorrect` which is expectedly different since "If there are two with the highest number of incorrect movement, you can pick any of them.", so with the randomness they will not be the same.
```python

# Load the parquet files
df_expected = pd.read_parquet("../data/features_expected.parquet")
df_actual = pd.read_parquet("../data/features.parquet")

# Find differing columns
differences = df_expected.compare(df_actual, keep_shape=True, keep_equal=False)
print("Columns with differences:", differences)
```

---
