import os
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

import os
import google.generativeai as genai
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

# CONFIGURAÇÃO FORÇADA
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Trocamos para 'gemini-pro' que é o "tanque de guerra" das APIs
model = genai.GenerativeModel('gemini-pro')

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
        # 1. O Twilio envia os dados como formulário, pegamos o campo 'Body'
        dados = await request.form()
        pergunta = dados.get("Body", "")
        
        # 2. Busca no estoque
        info_estoque = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    status = f"{qtd} unidades" if qtd > 0 else "Esgotado"
                    info_estoque += f"{loja}: {status}. "

        # 3. Gerar resposta com Gemini
        prompt = f"Você é o atendente da farmácia. Seja curto e educado. Pergunta: {pergunta}. Estoque atual: {info_estoque}"
        response = model.generate_content(prompt)
        texto_ia = response.text

        # 4. Formata para o WhatsApp (TwiML)
        twiml = MessagingResponse()
        twiml.message(texto_ia)
        
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        # Esse código vai te mandar o erro REAL no WhatsApp
        twiml = MessagingResponse()
        twiml.message(f"ERRO IDENTIFICADO: {str(e)}") 
        return Response(content=str(twiml), media_type="application/xml")