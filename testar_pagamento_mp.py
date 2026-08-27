import requests
import json
import webbrowser
import os

print("=== GERADOR DE PAGAMENTO SANDBOX (TESTE) ===")

# --- CONFIGURACAO ---
# Cole aqui o mesmo token TEST- que voce colocou no license_script.gs
ACCESS_TOKEN = "TEST-3305785757128662-022714-3d4fb9de18b5208d62072cd60b024635-390811379"
# --------------------

print(f"[DEBUG] Usando ACCESS_TOKEN: {ACCESS_TOKEN[:15]}...{ACCESS_TOKEN[-5:]}")

def gerar_link():
    if "COLE_SEU" in ACCESS_TOKEN:
        print("[ERRO] Voce precisa editar este arquivo e colocar seu ACCESS_TOKEN de teste na linha 10.")
        return

    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Cria uma preferencia de venda ficticia
    payload = {
        "items": [
            {
                "title": "Licenca Teste Seletor (Sandbox)",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 50.00
            }
        ],
        "back_urls": {
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com"
        },
        "auto_return": "approved",
        "notification_url": "https://script.google.com/macros/s/AKfycbxjfiuU0kW1HrYdM8HgfsAqqrNnXw1I0OHZYBjHNxcRUqAWUDN-sRd82VoBQJzc35ovgg/exec"
    }
    
    print("Criando preferencia de pagamento no Mercado Pago...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            data = response.json()
            link = data["sandbox_init_point"] # Forca o uso do link de sandbox direto
            
            print("\n=== LINK DE PAGAMENTO GERADO ===")
            print(link)
            print("================================")
            print("!!! ATENCAO - COMO EVITAR O BLOQUEIO DE EMAIL !!!")
            print("1. Abra o link em JANELA ANONIMA.")
            print("2. NAO FAÇA LOGIN (Se pedir email/senha, pule ou escolha 'Pagar como convidado').")
            print("3. Escolha a opcao 'Novo Cartao' ou 'Cartao de Credito'.")
            print("4. No campo E-MAIL, use um email DIFERENTE da sua conta Mercado Pago.")
            print("   (Se usar o mesmo email do vendedor, o pagamento sera recusado).")
            print("--------------------------------")
            print("DADOS PARA PREENCHER:")
            print("OPCAO 1 (VISA):")
            print("   Numero: 4111 1111 1111 1111")
            print("OPCAO 2 (MASTERCARD - Tente este se o Visa falhar):")
            print("   Numero: 5123 4567 8901 2345")
            print("--------------------------------")
            print("Nome: APRO")
            print("Validade: 11/2030  |  CVV: 123")
            print("CPF: Gere um CPF valido em qualquer site gerador (ex: 4devs) se pedir.")
            
            # webbrowser.open(link)
        else:
            print("Erro ao criar pagamento:", response.text)
    except Exception as e:
        print("Erro de conexao:", e)

if __name__ == "__main__":
    gerar_link()