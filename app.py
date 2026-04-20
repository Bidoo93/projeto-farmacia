import os
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

# Configuração da API
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Usamos o modelo 1.5-flash com o nome completo para não ter erro
model = genai.GenerativeModel('models/gemini-1.5-flash')

app = FastAPI()

estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

@app.get("/")
def home():
    return {"status": "Sistema Online", "local": "Esteio"}

@app.post("/whatsapp")
async def webhook(request: Request):
    try:
        # Twilio envia como formulário
        form_data = await request.form()
        pergunta = form_data.get("Body", "")
        
        # Busca no estoque
        info_estoque = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    info_estoque += f"{loja}: {qtd} unidades. "

        prompt = f"Você é o atendente da farmácia do Rodrigo. Responda de forma curta: {pergunta}. Estoque: {info_estoque}"
        
        # Chamada da IA
        response = model.generate_content(prompt)
        texto_ia = response.text

        # Resposta para o WhatsApp
        twiml = MessagingResponse()
        twiml.message(texto_ia)
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message(f"Erro: {str(e)}")
        return Response(content=str(twiml), media_type="application/xml")