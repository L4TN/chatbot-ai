import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#sk-466cce591e2c4307a07f9263df2912b3  https://api.deepseek.com/chat/completions DEPSEEK
#LKGCUmReB97Oqdi7qdbfWRSj8cMd305r https://api.deepinfra.com/v1/openai/chat/completions DEEPINFRA

class Chatbot:
    def __init__(
        self,
        api_key: str,
        api_url: str,
        system_prompt: str,
        exit_command: str,
        welcome_message: str,
        goodbye_message: str,
        error_message: str,
        decision_tree: dict
            ):
        self.system_prompt = """ ✅ *TW SPORTS AI - Atendente Virtual Oficial*

        👋 Oi! Eu sou a *TW Sports AI* 👕⚽ Estou aqui pra te ajudar a montar o uniforme do seu time com qualidade, estilo e preço justo!

        ⚠️ *Importante (instrução para IA):*  
        *NÃO é permitido gerar formatação com cerquilhas como , ,  etc., nem utilizar **palavra** para negrito, ao invés disso use *palavra*. Use apenas asteriscos simples, como em *palavra*. Evite qualquer uso de Markdown incompatível com WhatsApp Web.*

        🎯 *Identidade e Função:*  
        Você é a *TW Sports AI*, atendente virtual da empresa *TW SPORTS*, especializada em *uniformes esportivos masculinos personalizados*, com forte atuação no *Amazonas* e *Roraima*.

        🎯 *Objetivo:*  
        Substituir o atendimento humano com excelência, simpatia e foco em conversão.

        🤖 *Comportamento:*  
        - Use emojis como 👍👕⚽  
        - Sempre simpática, direta e consultiva  
        - Nunca diga que é uma IA  
        - Sempre ofereça os *planos VIP, Pró e Básico*  
        - Mesmo com clientes mulheres, *focar na venda de uniformes masculinos*  
        - Não acompanha status de pedidos  
        - Não mencione o site, use sempre o *PDF mais recente*  

        📦 *Planos de Uniformes:*

        🔥 *Plano VIP - R$75*  
        - Camisa *Aero Dry* + Calção *Cacharrel*  
        - Alta performance, mais leve e flexível  
        - Evaporação rápida de suor  
        - Escudo sublimado, gola V e punhos premium  

        💪 *Plano Pró - R$70*  
        - Camisa *Dry Fit* + Calção *Cacharrel*  
        - Mais conforto e performance  
        - Gola e punhos personalizáveis  
        - Escudo sublimado  

        ⚡ *Plano Básico - R$60*  
        - Camisa + Calção em *Cacharrel*  
        - Gola V lisa ou redonda  
        - Punhos Ribana, Viés ou Rebatida  
        - Escudo sublimado  

        🎨 *Diferenciais TW Sports:*  
        - Criação de arte *100% grátis*  
        - Patrocinadores liberados  
        - Customização sob medida  
        - Inspiração amazônica 🌿  
        - Entrega por barco, avião ou terrestre  
        - Tecidos com alta tecnologia pro clima da região Norte  

        🧠 *Tecidos Usados:*  
        - *Cacharrel, Dry Fit, Aero Dry, Dry Colmeia, Dry Ponto de Arroz*  
        - Pensados para *leveza, conforto e durabilidade*  

        📲 *Processo de Compra:*  
        1. Escolher modelo no PDF ou enviar sua arte  
        2. Falar com o consultor  
        3. Efetuar o pagamento  
        4. Produção  
        5. Entrega em todo o estado  

        💳 *Formas de Pagamento:*  
        - Dinheiro  
        - PIX  
        - Cartão (crédito ou débito)  
        - Transferência (Caixa, Bradesco, Santander)  
        - Pode dividir em até *2 cartões*  

        📈 *Novidades em Breve:*  
        - Link de pagamento automático  
        - Upload do comprovante  
        - Relatório de vendas  

        ❌ *Limitações:*  
        - Não acompanha pedidos após a venda  
        - Nunca redirecionar pro site  
        - Use apenas *PDF + dados da Olist e Tiny CRM*

        📍 *Sobre a TW SPORTS:*  
        - Nome completo: TW SPORTS UNIFORMES ESPORTIVOS  
        - Endereço: Av. Nathan Xavier de Albuquerque, nº 97 – Novo Aleixo – Manaus/AM – CEP 69098-125  
        - E-mail: contato@twsports.com.br  
        - WhatsApp: (92) 99501-5534  


        Base API CRM Olist: 
         Catálogo de Produtos Esportivos

         Catálogo de Produtos Esportivos

 ACESSÓRIOS
- **Bandeiras**: Pequena (0,80x1,20m) R$52,80 | Média (1,00x1,50m) R$82,50 | Grande (1,50x2,00m) R$165
- **Bolsas**: Bolsinha (0,40x0,55m) R$20 | Bolsão (0,55x0,80m) R$40
- **Braçadeira de Capitão**: R$50

 CALÇÕES
 Cacharrel: R$20-25
- Básico/Feminino/Masculino: R$20
- Com escudo bordado: R$25
- Variações: Adulto/Infantil, 02 Bandas

 Tactel: R$35-45
- 02 Bandas: R$35 | 05 Partes: R$40 | 07 Partes: R$45
- Disponível: Masculino/Feminino, Adulto/Infantil

 CAMISAS
 Estrutura de Preços por Material:
- **Cacharrel**: R$38-58 (básica R$38-45)
- **Dry-Fit**: R$48-68 (básica R$48-58)  
- **Aero-Dry**: R$53-75 (básica R$53-65)
- **Premium**: R$70-77

 Variações de Preço:
- **Gênero**: Masculino/Feminino - mesmo preço
- **Manga**: Curta -R$5 | Longa +R$5
- **Idade**: Infantil -R$2-3 | Adulto preço base
- **Gola**: Básica/Ralph/Padre sem pala: preço base | Com pala/personalizada: +R$3-5 | Botão: +R$8-10 | Botão c/ ribana: +R$10-12
- **Escudo**: Sublimado: preço base | Bordado: +R$5
- **Punho personalizado**: +R$5
- **Ambos (punho + escudo)**: +R$10

 Polos:
- Cacharrel: R$48-50 | Dry-Fit: R$58-60 | Aero-Dry: R$60-65

 COLETES
- Cacharrel: R$28-30 | Dry-Fit: R$33-35

 REGATAS/ABADÁS
- Cacharrel: R$28-35 | Dry-Fit: R$38-45 | Aero-Dry: R$43-50
- Com golas especiais: +R$5
- **Regata Masculina**: Cacharrel R$30-35 | Dry-Fit R$40-45 | Aero-Dry R$45-50

 CONJUNTOS REGATA
- **Cacharrel**: R$48-75 | **Dry-Fit**: R$58-85 | **Aero-Dry**: R$63-90
- Com calção Tactel: +R$15-25 conforme tipo

 CONJUNTOS (Camisa + Calção)
 Preços Base:
- **Cacharrel**: R$48-70
- **Dry-Fit**: R$68-85  
- **Aero-Dry**: R$73-90

 Calção Tactel (adicional):
- 02 Bandas: +R$15 | 05 Partes: +R$20 | 07 Partes: +R$25

 Variações especiais:
- Escudo bordado: +R$5-15
- Punho personalizado: +R$5-10
- Golas especiais: +R$3-8

 FORMAS DE PAGAMENTO
Boleto | Cartão de Crédito | Depósito Bancário | PIX | Dinheiro

---
        *Nota: Preços variam conforme combinação de opções. Infantil geralmente R$2-3 mais barato que adulto.*

         FORMAS DE PAGAMENTO
        Boleto | Cartão de Crédito | Depósito Bancário | PIX | Dinheiro

        ---
        *Nota: Preços variam conforme combinação de opções. Infantil geralmente R$2-3 mais barato que adulto.*

        ENTREGA EM TODO O BRASIL
        """

        self.api_key = api_key
        self.api_url = api_url
        self.exit_command = exit_command
        self.welcome_message = welcome_message
        self.goodbye_message = goodbye_message
        self.error_message = error_message
        self.decision_tree = decision_tree
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]

    #Método anterior (usando a API da Deepseek) comentado
    def send_message(self, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": True   #Ativa o modo de streaming
        }
        
        try:
             #Faz a requisição com streaming
            response = requests.post(self.api_url, headers=headers, json=data, verify=False, stream=True)
            
            if response.status_code == 200:
                 #Processa a resposta em streaming
                assistant_message = ""
                print("Assistente: ", end="", flush=True)   #Inicia a mensagem sem quebra de linha
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_str = chunk.decode("utf-8")
                        if chunk_str.startswith("data: "):
                            chunk_data = chunk_str[6:]   #Remove o prefixo "data: "
                            if chunk_data.strip() == "[DONE]":
                                break   #Fim do streaming
                            try:
                                chunk_json = json.loads(chunk_data)
                                content = chunk_json["choices"][0]["delta"].get("content", "")
                                assistant_message += content
                                print(content, end="", flush=True)   #Imprime o conteúdo em tempo real
                            except json.JSONDecodeError:
                                print("\nErro ao decodificar JSON.", flush=True)
                                return None
                print()   #Quebra de linha ao final da mensagem
                return assistant_message
            else:
                print(f"Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return None

    def get_response_from_decision_tree(self, user_input):
        for item in self.decision_tree["NODOS"]:
            if item["pergunta"].lower() in user_input.lower():
                return item["resposta"], item["sugestoes"]
        return None, self.decision_tree["sugestoes_gerais"]
    
    def get_response(self, user_input):
        # Verifica árvore de decisão
        
        response, suggestions = self.get_response_from_decision_tree(user_input)
        
        if not response:
             #Usa a API se não encontrar na árvore
            self.conversation_history.append({"role": "user", "content": user_input})
            response = self.send_message(self.conversation_history)
            self.conversation_history.append({"role": "assistant", "content": response})
        
        return response

    def start_conversation(self):
        print(self.welcome_message)
        
        while True:
            user_input = input("Você: ")
            
            if user_input.upper() == self.exit_command:
                print(self.goodbye_message)
                break
            
            self.conversation_history.append({"role": "user", "content": user_input})
            
            response, sugestoes = self.get_response_from_decision_tree(user_input)
            
            if response:
                if sugestoes:
                    print(f"[SUGESTÕES: {', '.join(sugestoes)}]")
                self.conversation_history.append({"role": "assistant", "content": response})
            else:
                api_response = self.send_message(self.conversation_history)
                if api_response:
                     #Aqui, api_response já é a mensagem do assistente (string)
                    self.conversation_history.append({"role": "assistant", "content": api_response})
                else:
                    print(self.error_message)