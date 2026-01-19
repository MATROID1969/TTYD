from openai import OpenAI
import os


def is_followup(previous_question: str, new_question: str) -> bool:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are classifying user intent.

Previous question:
"{previous_question}"

New question:
"{new_question}"

Is the new question a follow-up that modifies or refines the previous one
(e.g. "and women?", "only in Budapest", "only young people")?

Answer only YES or NO.
"""

    r = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return "YES" in r.choices[0].message.content.upper()
