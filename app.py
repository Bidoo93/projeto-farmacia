import os
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

# Configuração da API - Usando o método mais moderno
# Configuração da API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Trocamos para 'gemini-pro', ele é o mais estável e evita o erro 404
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

@app.get("/")
def home():
    return {"status": "Online", "msg": "Bora descansar Rodrigo!"}

@app.post("/whatsapp")
async def webhook(request: Request):
    try:
        # Pega a mensagem do WhatsApp
        form_data = await request.form()
        pergunta = form_data.get("Body", "")
        
        # Filtro de estoque
        info_estoque = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    info_estoque += f"{loja}: {qtd} unidades. "

        # IA responde
        prompt = f"Você é o atendente da farmácia. Responda curto: {pergunta}. Estoque: {info_estoque}"
        response = model.generate_content(prompt)
        
        # Prepara a volta para o Zap
        twiml = MessagingResponse()
        twiml.message(response.text)
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message(f"Quase lá! Erro: {str(e)}")
        return Response(content=str(twiml), media_type="application/xml")