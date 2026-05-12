# 🛡️ SAP Firefighter Log Compliance Reviewer

An AI-powered assistant designed to automate the review of SAP Firefighter logs, built for the Seargin AI/ML CoE Technical Challenge. This system significantly reduces human review time while maintaining strict compliance standards for SOX audits.

## 🏗️ Architecture & Approach
The system uses a hybrid logic approach, combining deterministic checks with semantic AI analysis:
1. **Truncation & Preprocessing:** Large SAP logs are intelligently truncated to fit within LLM context limits (approx. 8,000 characters) to prevent API errors and control token usage.
2. **Groq API & Llama 3.1 8B:** Migrated to Groq for ultra-fast, cost-effective inference. The `llama-3.1-8b-instant` model was chosen for its optimal balance of speed and reasoning capabilities.
3. **Self-Healing JSON Engine:** A robust extraction layer that uses Regular Expressions (Regex) to pull valid JSON out of conversational LLM responses, ensuring pipeline stability even if the model hallucinates formatting.
4. **Pydantic Validation:** Guarantees the output strictly adheres to the required schema (`ReviewResult`), preventing downstream errors in the UI.
5. **Streamlit UI:** An interactive dashboard allowing the Controller to review AI predictions, inspect findings, and record their final decisions.

## 📜 Compliance Rule Catalog
The system implements the 10 mandatory baseline rules to detect security breaches and procedural errors:
* **Critical:** Debug & Replace activity (R-003), OS-level commands (R-005), and SoD conflicts (R-010).
* **High:** Self-approval (R-008), direct table modifications (R-004), and module mismatch (R-002).
* **Medium:** Vague reason codes (R-001), outside business hours (R-007), and excessive duration (R-009).

## 📊 Evaluation Results
Tested against the provided training set of 50 sessions:
* **Overall Accuracy:** 64%
* **Critical Recall (REJECT):** 100% (The model successfully flagged all critical security violations).
* **Takeaway:** The Llama 8B model excels at "Safety First" strict rejection, ensuring no critical issues are missed. However, it can struggle with the nuance required for `NEEDS_CORRECTION` verdicts, often leaning towards binary PASS/REJECT decisions.

## 🤖 AI Tooling & Collaboration
As encouraged by the challenge guidelines, this project was developed using modern AI coding assistants:
* **Cursor (IDE):** Utilized for rapid code generation, auto-completion, and structuring the initial architecture.
* **Google Gemini (Chat):** Acted as a "thought partner" and senior developer for architectural brainstorming, debugging complex API rate-limit issues, and crafting the Regex/Self-Healing JSON logic.
Leveraging these tools allowed for quick architectural pivots (e.g., migrating to Groq) and a strong focus on business logic and error handling.

## 🛠️ How to Run

1. **Install dependencies:**
   `pip install -r requirements.txt`

2. **Setup API Key:**
   For security reasons, the API key is not included in the repository. Please generate a free Groq API key at console.groq.com/keys and paste it into `reviewer.py` (replace `"WSTAW_SWOJ_KLUCZ_GROQ_TUTAJ"`).

3. **Generate Predictions:**
   `python generate_predictions.py --input_dir dataset_candidate/train/sessions --output_file predictions.jsonl`

4. **Run Evaluation:**
   `python dataset_candidate/eval.py --predictions predictions.jsonl --labels dataset_candidate/train/labels.jsonl`

5. **Launch the UI Dashboard:**
   `streamlit run app.py`

## ⚠️ Known Failure Modes & Future Roadmap
* **Nuance Gap:** The model sometimes flags minor typos in reason codes as `REJECT` instead of `NEEDS_CORRECTION`.
* **Truncation Limitations:** Very large logs might lose context if critical actions happen at the very end of a 10,000+ character session.
* **Self-Approval False Positives:** The model occasionally struggles with precise string matching for the `firefighter_user` and `ticket_requester` fields (R-008), leading to lower precision on this specific rule.

**Next Steps (If given another week):**
1. Implement **RAG (Retrieval-Augmented Generation)** to provide the AI with a client-specific allowed transaction matrix.
2. Implement **Model Routing**: Use a fast, small model (like 8B) for initial triage, and route complex `NEEDS_CORRECTION` cases to a larger model (e.g., Llama 70B).
3. Move deterministic checks (like R-007 and R-008) completely to pure Python logic to save LLM tokens and ensure 100% accuracy.