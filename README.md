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
✔️ **Create unit tests for all transformations done**  
✔️ **Validate alignment with `features_expected.parquet`**  

---

## **🛠 Transformation Pipeline Overview**  

### **1. Data Aggregation & Grouping**  
- Collected **patient session data**.  
- Grouped by **`session_group`** to unify related exercises into a single record.  

### **2. Feature Engineering**  
- Created new **session-level metrics**:  
  - **`leave_exercise_*`** (number of left exercises).
  - **`prescribed_repeats*`** (number of repetitions supposed to perform). 
  - **`training_time`** (total session duration).  
  - **`perc_correct_repeats`** (accuracy percentage).  
  - **`number_exercises`** (total exercises performed).  
  - **`number_of_distinct_exercises`** (unique exercises).  

### **3. Handling Missing & Edge Cases**  
- Used **`COALESCE`** to fill missing values.  
- Ensured divisions avoid **`NULL` errors** using **`NULLIF`** in calculations.  

### **4. Ranking & Selection**  
- Identified **`exercise_with_most_incorrect`** using **ranking logic**.  
- **Randomly selected** an exercise in case of ties.  

### **5. Identifying Skipped Exercises**  
- Tracked **`first_exercise_skipped`** by ordering skipped exercises.  
- Selected the **first occurrence** using **`ROW_NUMBER()`**.  

### **6. Data Merging & Final Assembly**  
- **Merged all derived metrics** using **`LEFT JOIN`**.  
- Ensured **comprehensive session information** was retained.  

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
✔ **Unit tests where done for all SQL Queries (`test_transformations.py`)**  


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
