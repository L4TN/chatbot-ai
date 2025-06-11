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
        decision_tree: dict,
        rag_catalog: str = None
            ):
        # Combine system prompt with RAG catalog if provided
        if rag_catalog:
            self.system_prompt = f"{system_prompt}\n\n# CATÁLOGO E INFORMAÇÕES TÉCNICAS:\n{rag_catalog}"
        else:
            self.system_prompt = system_prompt

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
        
        if response:
            # Se encontrou na árvore de decisão, usa essa resposta
            return response
        else:
            # Usa a API se não encontrar na árvore
            self.conversation_history.append({"role": "user", "content": user_input})
            api_response = self.send_message(self.conversation_history)
            if api_response:
                self.conversation_history.append({"role": "assistant", "content": api_response})
                return api_response
            else:
                return self.error_message

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
