import os
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

# Configuração da API
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# FUNÇÃO PARA ACHAR O MODELO CERTO AUTOMATICAMENTE
def get_available_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return 'gemini-1.5-flash' # fallback caso a lista falhe

# Seleciona o modelo que o seu sistema permitir
model_name = get_available_model()
model = genai.GenerativeModel(model_name)

app = FastAPI()

estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

@app.get("/")
def home():
    return {"status": "Online", "modelo_usado": model_name}

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
        response = model.generate_content(prompt)
        
        twiml = MessagingResponse()
        twiml.message(response.text)
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message(f"DEBUG: Modelo {model_name} - Erro: {str(e)}")
        return Response(content=str(twiml), media_type="application/xml")