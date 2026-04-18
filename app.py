import os
import google.generativeai as genai
from fastapi import FastAPI, Request

# Pega a chave do Render
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Usaremos apenas o nome do modelo, sem o prefixo 'models/' 
# O Gemini Pro é o mais compatível com todas as chaves
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

@app.get("/")
def home():
    return {"status": "Farmacia Online Ativa"}

@app.post("/whatsapp")
async def webhook(request: Request):
    try:
        dados = await request.json()
        pergunta = dados.get("message", "Olá")
        
        # Filtro básico de estoque
        resumo = ""
        for loja, itens in estoques.items():
            for produto, qtd in itens.items():
                if produto in pergunta.lower():
                    resumo += f"{loja}: {qtd} unidades. "

        prompt = f"Atenda o cliente de forma curta. Pergunta: {pergunta}. Estoque: {resumo}"
        
        # Aqui está o segredo: vamos forçar a geração simples
        response = model.generate_content(prompt)
        return {"reply": response.text}
        
    except Exception as e:
        return {"error": str(e)}