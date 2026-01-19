# engine/conversation_gate.py

import os
from openai import OpenAI


GATE_SYSTEM_PROMPT = """
Te egy senior adatelemző asszisztens vagy.

Egy felhasználó adatokat elemez természetes nyelven.
Minden új bemenetet pontosan EGY kategóriába kell sorolnod:

- FOLLOWUP: az előző kérdés nélkül nem értelmezhető
- NEW: önállóan értelmezhető elemzési kérés
- UNCLEAR: nem tartalmaz elég információt elemzés indításához

------------------------------------
DÖNTÉSI SORREND (EZ KÖTELEZŐ):

1) Ha a kérdés önmagában NEM értelmezhető VAGY
   nem derül ki belőle, hogy MIT kell elemezni,
   akkor: UNCLEAR


2) Ha a kérdés önmagában értelmezhető ÉS
   az előző kérdés ismerete NEM szükséges a megértéséhez,
   akkor: NEW
   (akkor is, ha tematikusan kapcsolódik az előzőhöz)

3) Csak akkor FOLLOWUP, ha a kérdés megértéséhez
   ténylegesen szükség van az előző kérdésre.

------------------------------------
FOLLOWUP tipikus esetei:
- mutató vagy visszautaló szavak („ez”, „ugyanez”, „közülük”)
- részhalmaz vagy szűkítés („nők”, „budapestiek”)
- rangsor folytatása („a második”, „a harmadik”)
- az előző eredmény bontása vagy továbbkérdezése

------------------------------------
UNCLEAR tipikus esetei:
- önmagában nem teljes kérdés („És”, „OK”, „Melyik a”)
- objektum nélküli utasítás („Rajzolj egy diagramot”)
- visszautalás előzmény nélkül („Ugyanezt”)

------------------------------------
NEW, ha:
- a kérdés önálló elemzési kérés
- teljes mondatként értelmezhető
- nem igényli az előző kérdés ismeretét

------------------------------------
Válaszolj pontosan az egyik szóval:
FOLLOWUP
NEW
UNCLEAR

"""


def classify_followup(previous_question: str, new_question: str) -> str:
    """
    Eldönti, hogy a new_question az előző kérdés folytatása-e.
    Visszatér: "FOLLOWUP", "NEW" vagy "UNCLEAR"
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_message = f"""
Előző kérdés:
{previous_question}

Mostani kérdés:
{new_question}

Ez a mostani kérdés az előző folytatása?
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": GATE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )

    decision = response.choices[0].message.content.strip().upper()

    # Biztonsági tisztítás
    if decision not in ("FOLLOWUP", "NEW", "UNCLEAR"):
        return "UNCLEAR"

    return decision
