# **🏋️ Data Transformation and AI in physiotherapy**
> **Data Transformation and AI Message Generation Pipeline**

## **📌 Index**
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Branching Strategy](#branching-strategy)
4. [Setup Instructions](#setup-instructions)
5. [Data Transformation](#data-transformation)
6. [AI Message Generation](#ai-message-generation)
7. [Future Considerations](#future-considerations)
8. [Additional Reflections](#additional-reflections)

---

## Project Overview
This project automates **patient follow-up messaging** based on **session performance data** by leveraging:
- **Data Transformation:** Aggregating raw session data (`exercise_results.parquet`) into a structured format using **DuckDB & SQL**.
- **AI Message Generation:** Generating **personalized messages** for patients using **OpenAI GPT-4**.

The goal is to:
✔️ **Enable data-driven decision-making** for PTs  
✔️ **Ensure consistent & engaging** patient communication  
✔️ **Reduce manual workload** by automating messaging  

---
## Repository Structure
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
│   ├── features.sql                
│── tests/                          # Unit tests for queries
│   ├── test_transformations.py 
│── Makefile                        # Command-line automation
│── README.md                       # Project documentation
```

---

## Branching Strategy
This project follows a **feature-branch workflow**:

| Branch                          | Purpose                                   |
|---------------------------------|-------------------------------------------|
| **main**                        | Stable production-ready code              |
| **feature/data-transformation** | Question 1                                |
| **feature/ai-generated-message**| Question 2                                |
| **Documentation**               | Organizing Readme                         |

Merging was done via **separate PRs per feature branch** to keep changes modular and reviewable, and to simmulate real productization scenario.

---

## Setup Instructions
### **Clone the repository**
```bash
git clone https://github.com/joaovasco01/sword-ml-engineer-challenge.git
cd ml-engineer-test
```

### **Create & Activate Virtual Environment**
```bash
make venv  # Automatically creates and activates a virtual environment
source venv/bin/activate 
```

### **Install Dependencies**
- **Install required packages:**
  ```bash
  pip install pytest  # Required for running tests
  pip install tiktoken  # Needed for counting tokens for pricing
  pip install certifi  # Required for running async operations in Jupyter Notebook
  ```

- **Run tests:**
  ```bash
  python -m pytest tests/test_transformations.py
  ```

### **Setup Environment Variables**
Create a `.env` file in the project root:
Add your **OpenAI API Key** inside `.env`:
```
OPENAI_API_KEY=your-openai-key-here
```

---

## Data Transformation

### **💡 Key Objectives**
✔️ **Convert raw exercise records into structured session-level features**  
✔️ **Compute essential performance metrics** (e.g., `perc_correct_repeats`, `training_time`, `quality_rating`)  
✔️ **Identify skipped exercises & the most incorrect movements** 
✔️ **Create unit tests for all transformations done**  
✔️ **Validate alignment with `features_expected.parquet`**  


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

## AI Message Generation

### **🎯 Goal**
✔️ **Automate the generation of AI-crafted messages** for physical therapy patients.  
✔️ **Ensure high personalization** based on session performance & patient context.  
✔️ **Mimic human-written messages** while adhering to tone & structure guidelines.  
✔️ **Incorporate retry mechanisms** for OpenAI API rate limits & error handling.
✔️ **Token usage & cost estimation (EXTRA)** for API calls.  

### **🛠 Implementation Overview**

### **Fetching & Structuring Session Data**
- Retrieved **patient session details** using `fetch_session_data(session_group)`.  
- Ensured a **well-structured dictionary** containing:  
  - **Patient & session metadata** (e.g., `patient_name`, `therapy_name`, `session_number`).  
  - **Performance metrics** (e.g., `pain`, `fatigue`, `quality_rating`).  
  - **Exercise-specific insights** (`exercise_with_most_incorrect`, `first_exercise_skipped`).  

### **Scenario-Based Prompt Selection**
- Implemented **dynamic prompt selection** based on session status, basing the variables as personalizations on the text:
  - **OK Sessions:** Reinforce motivation, collect feedback, and guide future sessions.  
  - **NOK Sessions:** Downplay technical issues, acknowledge struggles, and ask open-ended questions.  
- Loaded & formatted **scenario prompts dynamically**:
  ```python
  session_context["scenario_description"] = get_scenario_prompt(session_context)
  ```

### **Message Personalization & Prompt Engineering**
- Leveraged **few-shot examples** to fine-tune AI message outputs.  
- Structured prompts following a **predefined system template**:  
  - **Conversational & empathetic tone**.  
  - **Avoid redundancy, clinical jargon, or formalities**.  
  - **Break messages into readable segments**.  
- Loaded & formatted the **user prompt template**:
  ```python
  user_prompt_template = load_prompt("user_prompt.txt")
  user_prompt = user_prompt_template.format(**session_context)
  ```

### **AI Message Generation**
- Integrated **OpenAI GPT-4 Turbo API** for text generation.
- Set **temperature = 0.7 to introduce controlled randomness**, ensuring that even if a session is exactly the same, the generated message varies slightly making it feel more natural and human-like. 
- Implemented robust **error handling & retry mechanisms** for API rate limits using exponential backoff to ensure reliability in asynchronous API calls:
  ```python
  for attempt in range(MAX_RETRIES):
      try:
          chat_completion = await openai.ChatCompletion.acreate(**kwargs)
          return chat_completion.choices[0].message[OpenAIKeys.CONTENT]
      except RateLimitError:
          if attempt < MAX_RETRIES - 1:
              wait_time = 2 ** attempt + random.uniform(0, 1)
              await asyncio.sleep(wait_time)  
          else:
              raise  
  ```

### **Token Optimization & Cost Estimation**
- Implemented **token counting & cost estimation** for API usage monitoring, to be able to understand pricing:
  ```python
  def count_tokens(text: str, model="gpt-4-turbo-preview") -> int:
      enc = tiktoken.encoding_for_model(model)
      return len(enc.encode(text))

  def estimate_cost(input_tokens: int, output_tokens: int, model="gpt-4-turbo-preview") -> float:
      input_cost = input_tokens * PRICING[model]["input"]
      output_cost = output_tokens * PRICING[model]["output"]
      return input_cost + output_cost
  ```

### **Message Generation API Execution**
- Final message generation pipeline executed asynchronously:
  ```python
  @app.command()
  async def get_message(session_group: str) -> str:
      session_context = fetch_session_data(session_group)
      if not session_context:
          return ""
      session_context["scenario_description"] = get_scenario_prompt(session_context)
      user_prompt = load_prompt("user_prompt.txt").format(**session_context)
      return await generate_message(user_prompt)
  ```

- To test message generation, open `message-generation.ipynb` and run it with two different sessions:  

  - **NOK (Needs Improvement)**:  
    ```
    Hey Taylor,

    Great job finishing your shoulder session #6! 🌟 You nailed those 8 exercises, which is fantastic. I see the shoulder abduction gave you a bit of a challenge. That's totally okay; those movements can be tough, especially as we're building up strength and flexibility.

    Noticing your pain at a 6 and fatigue at a 4, it sounds like you're pushing through, but let's keep an eye on that. We want to ensure we're challenging ourselves without overdoing it. Your overall quality rating is solid, so you're definitely on the right track!

    Given the struggle with shoulder abduction, let's focus on technique next time. Sometimes, a slight adjustment can make a big difference in how an exercise feels. Remember, it's all part of the process.

    How do you feel about your session today?
    ```

  - **OK (Successful Session)**:  
    ```
    Hey Michael,

    Wow, session #166 under your belt - that's incredible! Your dedication is truly paying off, and those numbers are looking sharp. 🌟 With such high accuracy, you're really mastering the movements, and it's great to see your pain and fatigue levels staying low. That's a sweet spot you want to maintain.

    Staying consistent is key, and you're nailing it. Each session builds on the last, and you're proving just how much progress can be made with steady effort.

    I'm curious, what's been the most rewarding part of this journey for you so far?
    ```

---

## Future Considerations

While the current implementation provides **automated AI-generated messages** and **session-level insights**, there are several areas for **scalability and improvement**:

### **🧠 1️⃣ Storing Context of Previous Sessions (RAG)**
- Implement a **Retrieval-Augmented Generation (RAG)** approach to **store patient session history** in a database.
- **Why?** This would allow AI to **reference past patient interactions**, ensuring **more personalized and context-aware messages**.
- **How?** Store session summaries in a database and pass relevant past sessions into the prompt dynamically.

### **🤖 2️⃣ Message Validation Agent**
- Introduce a **secondary validation agent** to review AI-generated messages.
- If the validation agent **disagrees with the message**, trigger a **second attempt** (up to **2 retries**).
- **Goal?** Ensure messages are **clinically accurate**, **context-aware**, and **follow PT guidelines** before being sent.

### **🔗 3️⃣ LangChain Integration for AI Workflow**
- **Enhance AI automation** by structuring the **AI messaging process** as a **multi-step agent-based workflow**.
- **LangChain** would allow:
  - **Dynamic prompt chaining** (e.g., fetching past session context before generating a message)
  - **External tool integration** (e.g., checking patient progress trends before crafting a message)
  - **Scalability for future enhancements**, such as **auto-adjusting tone** based on patient response patterns.

By implementing these enhancements, the pipeline will **improve personalization, validation, and automation**, ensuring **higher-quality patient engagement** with minimal PT intervention.

---

## Additional Reflections

This project was an excellent opportunity to **combine data engineering with AI-driven communication**, tackling **real-world challenges** faced by physical therapists. 

One of the most interesting aspects was handling **session-level aggregation and AI message structuring** to ensure both **accuracy and usability**. The **balance between data precision and conversational AI** was a fascinating problem to solve, making sure the AI-generated messages felt **natural, engaging, and useful**.

Beyond technical implementation, this challenge reinforced the value of **scalability, automation, and structured engineering workflows**. Exploring **LangChain, RAG-based memory, and AI validation agents** as future improvements would elevate this system even further.

## **🤝 Contributing & Contact**

This repository was created as part of a **technical assessment** and is not currently open for external contributions. However, I’m always open to **discussions, feedback, and suggestions** to improve the approach.

If you have any questions, feedback, or just want to chat about the project, feel free to reach out:

- **👤 Name**: João Vasco Almeida Sobral Siborro Reis  
- **📧 Email**: [joaovascoscp@gmail.com](mailto:joaovascoscp@gmail.com)  
- **🔗 LinkedIn**: [João Vasco](https://www.linkedin.com/in/joão-vasco-9a50331a6/)  
- **🐙 GitHub**: [joaovasco01](https://github.com/joaovasco01)  

Thanks for checking out my work!
