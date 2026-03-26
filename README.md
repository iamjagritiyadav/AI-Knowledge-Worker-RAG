# Insurellm AI: Enterprise RAG Knowledge Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=for-the-badge)

**Insurellm AI** is a high-performance Retrieval-Augmented Generation (RAG) system designed to provide instant, accurate answers from internal insurance policy documents.

Built with a focus on speed and accuracy, it features a parallel processing ingestion pipeline, a modern "Midnight Blue" dark-mode UI, and a strict "LLM-as-a-Judge" evaluation system to ensure enterprise-grade reliability.

---

## 🚀 Key Features

* **⚡ High-Speed Ingestion:** Utilizes parallel processing to ingest hundreds of documents per minute, leveraging `Gemini 2.0 Flash` and `Text-Embedding-004` for efficient vectorization.
* **🧠 Intelligent Routing:** Features a smart router that distinguishes between casual conversation (handled instantly) and technical queries (routed to the Vector DB).
* **🔍 Accurate Retrieval:** Powered by **ChromaDB** for persistent vector storage and **LiteLLM** for unified model orchestration.
* **📊 Automated Evaluation:** Includes a custom `evaluate.py` script that employs an "LLM-as-a-Judge" methodology to grade response accuracy against a golden dataset.
* **🎨 Modern Dark UI:** A professional, fully custom Streamlit interface featuring glassmorphism, high-contrast chat bubbles, and source citations.

---

## 🛠️ Tech Stack

* **LLM:** Google Gemini 2.0 Flash (via LiteLLM)
* **Embeddings:** Google Text-Embedding-004
* **Vector Database:** ChromaDB (Persistent storage)
* **Frontend:** Streamlit (Custom CSS Dark Mode)
* **Orchestration:** Python 3.11, Tenacity (Retries), Pydantic (Data Validation)

---
NOTE :- Knowledgebase used for rag implementaion is genrated using chatgpt. its not credible.
## 📂 Project Structure

```bash
├── app.py              # Main Streamlit frontend application
├── answer.py           # RAG Backend logic (Retrieval + Generation + Routing)
├── ingest.py           # High-speed document ingestion script
├── evaluate.py         # Automated accuracy testing (LLM-as-a-Judge)
├── requirements.txt    # Project dependencies
├── preprocessed_db/    # ChromaDB storage folder (Generated after ingestion)
└── .env                # API Keys (Not pushed to GitHub)
⚙️ Installation & Setup
1. Clone the Repository
Bash

git clone [https://github.com/your-username/insurellm-ai.git](https://github.com/your-username/insurellm-ai.git)
cd insurellm-ai
2. Create Virtual Environment
Bash

python -m venv .venv
source .venv/bin/activate  # On Mac/Linux
# .venv\Scripts\activate   # On Windows
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Configure API Keys
Create a .env file in the root directory and add your Google Gemini API key:

Ini, TOML

GEMINI_API_KEY="your-secret-key-here"
🏃‍♂️ Usage
1. Ingest Documents (Build the Brain)
If you have raw documents, place them in a knowledge-base folder and run:

Bash

python ingest.py
This processes documents in parallel and saves the vector store to preprocessed_db/.

2. Run the Web App
Launch the full UI in your browser:

Bash

python -m streamlit run app.py
3. Run Accuracy Evaluation
Test the bot's accuracy against "Gold Standard" questions:

Bash

python evaluate.py
Output: A generated report card with 1-5 scores for accuracy.

🌐 Deployment (Streamlit Cloud)
This project is optimized for Streamlit Community Cloud.

Push this code to GitHub (ensure preprocessed_db is included).

Connect your repo on share.streamlit.io.

Add your GEMINI_API_KEY in the Advanced Settings > Secrets menu.

Deploy! 🚀

📝 License
This project is licensed under the MIT License.
