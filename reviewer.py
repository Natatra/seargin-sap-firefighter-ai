"""SAP Firefighter session reviewer — Groq (Llama 8B) - Wersja Stabilna z poprawionym Promptem."""

from __future__ import annotations

import json
import re
import requests
from pydantic import ValidationError

from models import ReviewResult, SessionLog


SYSTEM_PROMPT = """You are an expert SAP Auditor performing SOX compliance reviews. 
Analyze the provided SAP session JSON log and output a structured verdict.

VERDICT LOGIC:
1. PASS: No rules violated.
2. NEEDS_CORRECTION: Used ONLY for minor justification issues (R-001, R-002, R-007, R-009).
3. REJECT: Used for critical security breaches (R-003, R-004, R-005, R-010) OR severe self-approval (R-008).

DETAILED RULES:
R-001 (medium): Reason code is empty, generic (test, fix, asd), or < 20 chars.
R-002 (high): Reason code mentions one system/module but transactions touch a different one.
R-003 (critical): Debug & replace activity (/h in SM21 or field changes in debugger).
R-004 (high): Direct table modification (SE16N edit, SM30) without specific ticket reference.
R-005 (critical): OS-level commands used (SM49, SM69).
R-006 (high): Transaction count is abnormally high for the stated reason.
R-007 (medium): Session outside business hours (Mon-Fri 8:00-17:00) without emergency note.
R-008 (high): Self-approval. TRIGGER ONLY IF 'firefighter_user' is EXACTLY THE SAME as 'ticket_requester'.
R-009 (medium): Duration > auto-extend limit (e.g., > 4 hours).
R-010 (critical): SoD conflict (e.g., vendor master change + payment execution).

OUTPUT INSTRUCTIONS:
- Return ONLY a valid JSON object.
- JSON structure:
{
  "session_id": "string",
  "verdict": "PASS" | "REJECT" | "NEEDS_CORRECTION",
  "findings": [
    { "rule_id": "string", "severity": "low" | "medium" | "high" | "critical", "location": "string", "description": "string", "evidence": "string" }
  ],
  "suggested_correction": { "message_to_firefighter": "string", "suggested_reason_rewrite": "string" }
}"""


class FirefighterReviewer:
    def __init__(self, model: str | None = None) -> None:
        _ = model
        self.api_key = "Please provide your Groq API key"

    def analyze_session(self, session: SessionLog) -> ReviewResult:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        session_json = session.model_dump_json()
        if len(session_json) > 8000:
            session_json = session_json[:8000] + "... [TRUNCATED]"

        data = {
            "model": "llama-3.1-8b-instant", 
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this SAP session log: {session_json}"}
            ],
            "temperature": 0.1
        }
        
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json=data,
            timeout=30,
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Błąd API Groq {response.status_code}: {response.text}")
            
        body = response.json()
        raw_content = body["choices"][0]["message"]["content"]

        try:
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            clean_json = json_match.group(0) if json_match else raw_content
            
            data_dict = json.loads(clean_json)
            
            if "suggested_correction" not in data_dict or not data_dict["suggested_correction"]:
                data_dict["suggested_correction"] = {
                    "message_to_firefighter": "No correction needed.",
                    "suggested_reason_rewrite": "N/A"
                }
            else:
                if "message_to_firefighter" not in data_dict["suggested_correction"]:
                    data_dict["suggested_correction"]["message_to_firefighter"] = "No correction needed."
                if "suggested_reason_rewrite" not in data_dict["suggested_correction"]:
                    data_dict["suggested_correction"]["suggested_reason_rewrite"] = "N/A"

            return ReviewResult.model_validate(data_dict)
            
        except Exception as exc:
            raise RuntimeError(f"Błąd parsowania/naprawy JSON: {exc}\nTreść: {raw_content[:500]}")