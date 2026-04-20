import os
from google import genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

# O cliente da nova biblioteca 2026
# Ele já busca o GEMINI_API_KEY sozinho do ambiente do Render
client = genai.Client()

app = FastAPI()

estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

@app.get("/")
def home():
    return {"status": "Sistema Farmácia 2026 Online"}

@app.post("/whatsapp")
async def webhook(request: Request):
    try:
        form_data = await request.form()
        pergunta = form_data.get("Body", "")
        
        info_estoque = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    info_estoque += f"{loja}: {qtd} unidades. "

        prompt = f"Você é atendente da farmácia. Responda curto: {pergunta}. Estoque: {info_estoque}"
        
        # COMANDO OFICIAL GEMINI 3 FLASH
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt
        )
        
        twiml = MessagingResponse()
        twiml.message(response.text)
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message(f"Erro na API 2026: {str(e)}")
        return Response(content=str(twiml), media_type="application/xml")