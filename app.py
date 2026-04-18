import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

# Configuração do Gemini (Você vai precisar da sua API KEY do Google AI Studio)
genai.configure(api_key="AIzaSyAL2UtV6xpFfwm4Je6gs07MLkyPt_g1pLc")
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# Simulação de 3 Estoques de lojas diferentes
estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

def consultar_estoque_geral(remedio):
    # Função que a IA "chama" para ver os estoques
    remedio = remedio.lower()
    resultado = ""
    for loja, produtos in estoques.items():
        qtd = produtos.get(remedio, 0)
        status = f"{qtd} unidades" if qtd > 0 else "Esgotado"
        resultado += f"- {loja}: {status}\n"
    return resultado

@app.post("/whatsapp")
async def webhook(request: Request):
    dados = await request.json()
    pergunta_cliente = dados.get("message", "")

    # Prompt para o Gemini ser um atendente de farmácia
    prompt = f"""
    Você é o atendente virtual da farmácia. Seja educado e prestativo.
    Abaixo estão os dados reais do estoque para o produto que o cliente pediu:
    {consultar_estoque_geral(pergunta_cliente)}
    
    Responda ao cliente: "{pergunta_cliente}" informando a disponibilidade nas lojas.
    Se estiver esgotado em todas, sugira que ele aguarde a reposição amanhã.
    """

    response = model.generate_content(prompt)
    return {"reply": response.text}