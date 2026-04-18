import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

# AGORA O CÓDIGO PEGA A CHAVE DO RENDER AUTOMATICAMENTE
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

# Estoques
estoques = {
    "Loja Esteio": {"dipirona": 10, "amoxicilina": 2, "protetor solar": 15},
    "Loja Sapucaia": {"dipirona": 0, "amoxicilina": 8, "protetor solar": 0},
    "Loja Canoas": {"dipirona": 5, "amoxicilina": 0, "protetor solar": 20}
}

def consultar_estoque_geral(mensagem):
    # Lógica simples para identificar o remédio na frase
    mensagem = mensagem.lower()
    remedios_conhecidos = ["dipirona", "amoxicilina", "protetor solar"]
    
    remedio_encontrado = "o produto solicitado"
    for r in remedios_conhecidos:
        if r in mensagem:
            remedio_encontrado = r
            break
            
    resultado = f"Estoque para: {remedio_encontrado}\n"
    for loja, produtos in estoques.items():
        qtd = produtos.get(remedio_encontrado, 0)
        status = f"{qtd} unidades" if qtd > 0 else "Esgotado"
        resultado += f"- {loja}: {status}\n"
    return resultado

@app.post("/whatsapp")
async def webhook(request: Request):
    try:
        dados = await request.json()
        pergunta_cliente = dados.get("message", "")

        contexto_estoque = consultar_estoque_geral(pergunta_cliente)
        
        prompt = f"""
        Você é o atendente virtual da farmácia. Seja educado e prestativo.
        Dados reais do estoque:
        {contexto_estoque}
        
        Pergunta do cliente: "{pergunta_cliente}"
        Responda informando a disponibilidade. Se estiver esgotado em tudo, sugira aguardar.
        """

        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"error": str(e)}