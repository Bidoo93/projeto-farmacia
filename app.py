import os
import google.generativeai as genai
from fastapi import FastAPI, Request

# Configuração da API
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# O segredo está aqui: usamos o modelo 1.5-flash que é o mais rápido e estável
model = genai.GenerativeModel('gemini-1.5-flash')

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
        dados = await request.json()
        pergunta = dados.get("message", "")
        
        # Busca no estoque
        info_estoque = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    info_estoque += f"{loja}: {qtd} unidades. "

        prompt = f"Você é o atendente da farmácia do Rodrigo. Responda de forma curta: {pergunta}. Estoque: {info_estoque}"
        
        # Chamada da IA
        response = model.generate_content(prompt)
        return {"reply": response.text}
        
    except Exception as e:
        return {"error": str(e)}