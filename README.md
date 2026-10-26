\# CareCloud Voice AI Patient Registration



\## Live Demo \& Credentials

\- \*\*Phone Number:\*\* +1 (585) 577-2007 \*(Note: If the carrier fails to provision the free Vapi number, please use the Web Call test link in the Vapi dashboard).\*

\- \*\*API Base URL:\*\* https://jaunt-trade-shortage.ngrok-free.dev \*(Note: This is a live ngrok tunnel. If it is offline, run `uvicorn main:app` and `ngrok http 8000` locally).\*

\- \*\*Dashboard:\*\* https://jaunt-trade-shortage.ngrok-free.dev/dashboard



\## Architecture

\- \*\*Telephony/Voice:\*\* Vapi (Free inbound number + Web Call)

\- \*\*LLM:\*\* Groq (Llama 3.3 70B Versatile)

\- \*\*Backend:\*\* FastAPI + SQLAlchemy

\- \*\*Database:\*\* SQLite (file-based, persists across restarts)

\- \*\*Dashboard:\*\* HTML/JS served directly by FastAPI



\## How It Works

1\. The caller speaks to the Vapi agent.

2\. Vapi uses Groq (Llama 3) to converse naturally, validate inputs (e.g., 10-digit phone), and handle corrections.

3\. Upon caller confirmation, the LLM calls the `save\_patient` Vapi Tool.

4\. Vapi sends a POST request to `/tools/save-patient` on the FastAPI backend.

5\. FastAPI validates via Pydantic and writes to SQLite.

6\. The Dashboard polls `GET /patients` to display records.



\## Trade-offs \& Known Limitations

\- \*\*SQLite\*\* is used for zero-config persistence. In production, PostgreSQL would be better.

\- \*\*Telephony Issues:\*\* The Vapi free tier number experienced carrier provisioning delays (callers heard "forwarded to automated system"). The Voice Agent logic is fully functional and verified via Vapi's Web Call feature.

\- \*\*API Validation:\*\* Currently, PUT requests replace the whole record. A PATCH implementation would be better for true partial updates.

\- \*\*Ngrok:\*\* Used to expose the local backend for the assessment. 



\## Setup Instructions (Local)

1\. `python -m venv venv`

2\. `source venv/bin/activate` (or `venv\\Scripts\\activate` on Windows)

3\. `pip install -r requirements.txt`

4\. `uvicorn main:app --reload`

5\. `ngrok http 8000`

