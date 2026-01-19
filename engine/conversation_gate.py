# engine/conversation_gate.py

import os
from openai import OpenAI


GATE_SYSTEM_PROMPT = """
Te egy senior adatelemző asszisztens vagy.

Egy felhasználó adatokat elemez természetes nyelven.
Minden kérdés vagy:
- egy meglévő elemzés folytatása vagy módosítása (FOLLOWUP)
- egy teljesen új elemzés (NEW)
- vagy nem egyértelmű (UNCLEAR)

A feladatod:
Megmondani, hogy a mostani kérdés az előző kérdés folytatása-e.

FONTOS:  
A felhasználók gyakran nem ismétlik meg a témát, hanem mutató szavakat használnak
(pl. „ez”, „ugyanez”, „a második”, „és?”, „közülük”).

Ilyenkor ez FOLLOWUP.

------------------------------------

FOLLOWUP, ha a mostani kérdés:
- az előző kérdés eredményére utal („ez”, „ugyanez”, „a második”, „következő”, „közülük”)
- egy részhalmazt ad hozzá (pl. „nők”, „férfiak”, „40 év felettiek”)
- egy meglévő elemzés bontását kéri
- rangsorban kérdez tovább („és a második?”, „mi a harmadik?”)
- vagy nyilvánvalóan az előző témára épít

------------------------------------

UNCLEAR, ha:
- a kérdés önmagában nem értelmezhető („és?”, „ugyanezt mutasd”)
- nem derül ki, mire vonatkozik, DE láthatóan utal valamire

FONTOS:
UNCLEAR csak akkor választható,
ha a mostani kérdésből SEMMILYEN
értelmezhető elemzési feladat nem vezethető le.
Ha a kérdésre akár leegyszerűsítve is
Python kód lenne generálható,
akkor NEM lehet UNCLEAR.


------------------------------------

NEW, ha:
- teljesen új témát hoz be
- más dologról kérdez, mint az előző (pl. úticél → gyorsétterem)
- és nem tartalmaz utalást az előző kérdésre

FONTOS:
Ha a mostani kérdés önálló elemzési feladatként
értelmezhető és futtatható lenne az előző kérdés nélkül,
akkor NEW-nek kell besorolni,
akkor is, ha tematikusan kapcsolódik az előző kérdéshez.

------------------------------------

Válaszolj pontosan az egyik szóval:
FOLLOWUP
NEW
UNCLEAR


=== RECEPTEK (példák) ===

1. Példa
 Kategória: NEW (önálló kérdés)

Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„Rajzolj egy diagramot a legnépszerűbb gyorséttermekről.”

Indoklás:
A mostani kérdés önállóan értelmezhető.
Új elemzési műveletet kér (vizualizáció).
Nem szükséges az előző kérdés a megértéséhez.

Besorolás: NEW

2. Példa
Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„Hány százalék eszik naponta csokoládét?”

Indoklás:
Teljesen új téma.
Az előző kérdés irreleváns.
Önálló statisztikai kérdés.

Besorolás: NEW


3. Példa
Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„És a nők között?”

Indoklás:
A mostani kérdés önmagában nem értelmezhető.
Nem nevezi meg az elemzett objektumot.
Csak az előző kérdés kontextusában érthető.

Besorolás: FOLLOWUP


4. Példa
Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„És a második?”

Indoklás:
Rangsor folytatására utal.
Az „a második” kizárólag az előző eredményhez képest értelmezhető.

Besorolás: FOLLOWUP

5. Példa
Előző kérdés:
„Hányan járnak Burger King-be?”

Mostani kérdés:
„A budapestiek közül?”

Indoklás:
Részhalmazt kér.
Nem derül ki önmagában, mit kell számolni.
Az előző kérdés nélkül nem értelmezhető.

Besorolás: FOLLOWUP


6. Példa
Előző kérdés:
„Mely országba terveznek legtöbben utazni?”

Mostani kérdés:
„És a diplomások közül?”

Indoklás:
Demográfiai szűkítést kér.
Az alapváltozó az előző kérdésből jön.

Besorolás: FOLLOWUP


7. Példa
Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„És”

Indoklás:
Nem tartalmaz elemzési célt.
Nem kérdez.
Nem utal egyértelműen konkrét folytatásra.

Besorolás: UNCLEAR

8. Példa
Előző kérdés:
„Hány százalék eszik naponta csokoládét?”

Mostani kérdés:
„OK”

Indoklás:
Nem elemzési kérdés.
Nem tartalmaz utasítást vagy kérést.

Besorolás: UNCLEAR

9. Példa
Előző kérdés:
„Melyik a legnépszerűbb gyorsétterem?”

Mostani kérdés:
„Melyik a”

Indoklás:
Befejezetlen kérdés.
Nem derül ki, mire vonatkozik.

Besorolás: UNCLEAR


=== DÖNTÉSI PRIORITÁS ===

1. Ha a mostani kérdés önálló elemzési feladatként értelmezhető → NEW
2. Ha a mostani kérdés csak az előző kérdés ismeretében értelmezhető → FOLLOWUP
3. UNCLEAR kizárólag akkor,
   ha sem az előző,
   sem önálló értelmezés nem lehetséges


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

A mostani kérdés besorolása az előző kérdéshez képest:
FOLLOWUP, NEW vagy UNCLEAR?

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
