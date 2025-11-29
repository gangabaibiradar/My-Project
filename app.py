# app.py
import streamlit as st
import os
import openai
import difflib
import time
import uuid
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def load_faqs(path="faqs.txt"):
    faqs = []
    if not os.path.exists(path):
        return faqs
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("---")
    for b in blocks:
        lines = [l.strip() for l in b.strip().splitlines() if l.strip()]
        q = ""
        a = ""
        for line in lines:
            if line.lower().startswith("q:"):
                q = line[2:].strip()
            elif line.lower().startswith("a:"):
                a = line[2:].strip()
        if q and a:
            faqs.append({"q": q, "a": a})
    return faqs

def best_faq_match(user_q, faqs, cutoff=0.6):
    if not faqs:
        return None, 0.0
    questions = [f["q"] for f in faqs]
    matches = difflib.get_close_matches(user_q, questions, n=1, cutoff=cutoff)
    if matches:
        matched_q = matches[0]
        idx = questions.index(matched_q)
        return faqs[idx]["a"], 1.0
    
    best_idx = None
    best_ratio = 0.0
    for i, q in enumerate(questions):
        ratio = difflib.SequenceMatcher(None, user_q.lower(), q.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i
    if best_ratio >= cutoff:
        return faqs[best_idx]["a"], best_ratio
    return None, best_ratio

ESCALATION_KEYWORDS = {
    "payment": ["payment failed", "refund", "charged", "unauthorized", "billing"],
    "account": ["password", "login", "account locked"],
    "technical": ["not working", "error", "bug", "crash"],
    "legal": ["legal", "data breach", "privacy"],
}

def keyword_classify(text):
    t = text.lower()
    for cat, kws in ESCALATION_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return cat, True
    for kw in ["angry", "complain", "sue"]:
        if kw in t:
            return "complaint", True
    return "general", False

def query_llm_answer(question, context=None):
    if not OPENAI_API_KEY:
        return "LLM disabled. Set OPENAI_API_KEY in .env file."

    prompt = f"""
You are a helpful customer support assistant.
Use this context to answer if helpful:

{context}

User question: {question}
Provide a clear and polite answer.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[Error contacting model] {e}"

def query_llm_classify(question):
    if not OPENAI_API_KEY:
        return {"category": "general", "escalate": False}

    system = """
Classify a support query.
Return JSON with:
- category: one word
- escalate: true/false
"""

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question}
            ],
            temperature=0.0,
            max_tokens=100
        )
        import json
        return json.loads(resp["choices"][0]["message"]["content"])
    except:
        return {"category": "general", "escalate": False}

TICKET_FILE = "tickets.csv"

def create_ticket(name, email, category, summary, details):
    ticket_id = str(uuid.uuid4())[:8]
    row = {
        "ticket_id": ticket_id,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "email": email,
        "category": category,
        "summary": summary,
        "details": details
    }
    df = pd.DataFrame([row])

    if os.path.exists(TICKET_FILE):
        old = pd.read_csv(TICKET_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(TICKET_FILE, index=False)
    return ticket_id

st.set_page_config(page_title="Support Assistant", layout="centered")
st.title("🛠 AI Support Assistant (Moderate Version)")

faqs = load_faqs("faqs.txt")

if "history" not in st.session_state:
    st.session_state.history = []

name = st.text_input("Your Name")
email = st.text_input("Email (optional)")
user_q = st.text_area("Enter your issue:", height=120)

if st.button("Submit"):
    st.session_state.history.append({"role": "user", "text": user_q})


    answer, score = best_faq_match(user_q, faqs, cutoff=0.65)
    if answer:
        st.success("Answered using FAQs")
        st.write(answer)
        st.session_state.history.append({"role": "assistant", "text": answer})
    else:
        
        category, escalate_local = keyword_classify(user_q)
        final_class = query_llm_classify(user_q)

        st.info(f"Category detected: *{final_class['category']}, Escalate: **{final_class['escalate']}*")

        
        ai_answer = query_llm_answer(user_q, context="Internal FAQ system available.")
        st.markdown("### AI Answer:")
        st.write(ai_answer)
        st.session_state.history.append({"role": "assistant", "text": ai_answer})

    
        if final_class["escalate"]:
            st.warning("This issue requires escalation. Creating a ticket...")
            summary = user_q[:100] + "..."
            ticket_id = create_ticket(name, email, final_class["category"], summary, user_q)
            st.success(f"Ticket Created: *{ticket_id}*")
        else:
            st.info("No escalation needed.")

st.markdown("---")
st.subheader("Chat History")
for m in st.session_state.history:
    if m["role"] == "user":
        st.markdown(f"🧑 *You:* {m['text']}")
    else:
        st.markdown(f"🤖 *Assistant:* {m['text']}")