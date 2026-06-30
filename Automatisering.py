"""
Lead-opvolging: ontvangt een RUWE, vrije tekst (zoals een echte e-mail van
een lead) en genereert automatisch een persoonlijk antwoord via Gemini.

Geen losse velden meer nodig (naam/bedrijf/interesse) - je plakt gewoon
de volledige tekst die de lead geschreven heeft, precies zoals een
echte e-mail/formulier dat ook zou binnenkomen.

Setup:
    pip install fastapi uvicorn google-genai --break-system-packages

Run:
    $env:GEMINI_API_KEY="MIJN API KEY"
    python lead_followup_vrije_tekst.py

Testen:
    Ga naar http://127.0.0.1:8000/docs
    Klik op /new-lead -> Try it out
    Vul bij "bericht" gewoon de vrije tekst van de lead in, bv:
    "Hallo ik hoorde dat jij een huis had die zou ik graag willen kopen"
    Klik Execute
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Lead Follow-up Generator (vrije tekst)")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class LeadBericht(BaseModel):
    bericht: str  # de volledige, vrije tekst die de lead geschreven heeft


def genereer_email(bericht: str) -> str:
    prompt = f"""Je bent een sales-assistent voor een makelaarskantoor.
Je krijgt hieronder een bericht van een potentiele klant (lead), in vrije tekst,
precies zoals diegene het zelf geschreven heeft (bv. via een contactformulier of mail).

Bericht van de lead:
\"\"\"{bericht}\"\"\"

Schrijf een kort, persoonlijk antwoord (max 120 woorden) terug aan deze lead.

Eisen:
- Haal zelf uit de tekst wat relevant is (naam indien genoemd, wat ze willen,
  context) en verwerk dat in je antwoord
- Vriendelijk en niet opdringerig
- Eindig met een lichte call-to-action (bv. kort telefoongesprek voorstellen
  of vragen naar meer details zoals budget/locatie)
- Geen overdreven salesjargon
- Schrijf in het Nederlands
- Geef ALLEEN de e-mailtekst terug, geen onderwerp, geen uitleg erbij
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


@app.post("/new-lead")
def new_lead(lead: LeadBericht):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY ontbreekt")

    email_tekst = genereer_email(lead.bericht)

    return {
        "ontvangen_bericht": lead.bericht,
        "gegenereerde_email": email_tekst,
    }


@app.get("/")
def root():
    return {"status": "Lead follow-up (vrije tekst) draait. Ga naar /docs om te testen."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)