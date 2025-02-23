# **🏋️ Sword ML Engineer Test**
> **End-to-End Data Transformation and AI Message Generation Pipeline**

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
│   ├── starter.ipynb               # Testing for Question 2
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