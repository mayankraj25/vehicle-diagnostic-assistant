from openai import OpenAI
from config import LLM_URL, LLM_MODEL

client=OpenAI(base_url=LLM_URL,api_key="ollama")

SYSTEM_PROMPT = """
You are an intelligent vehicle health assistant for a Hyundai Creta.
You have access to real-time engine telemetry and diagnostic data.
Speak naturally and conversationally as if talking directly to the driver.
Keep responses under 3 sentences — this is spoken output, not a report.
Always mention safety concerns first if any exist.
Never use bullet points or lists — speak in natural sentences only.
If everything is normal, say so clearly and briefly.
"""

def ask_llm(driver_question,context_events):
    if context_events:
        context_text="\n".join([f"[{e['timestamp']}],[{e['severity'].upper()}],[{e['event']}]" for e in context_events])
    else:
        context_text="No anomalies detected. All systems normal."

    prompt=f"Vehicle telemetry context:\n{context_text}\n \nDriver question: {driver_question}"

    response=client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":prompt}
        ],
        max_tokens=150,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()