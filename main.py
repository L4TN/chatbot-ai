import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
        self.api_key = api_key
        self.api_url = api_url
        self.system_prompt = system_prompt
        self.exit_command = exit_command
        self.welcome_message = welcome_message
        self.goodbye_message = goodbye_message
        self.error_message = error_message
        self.decision_tree = decision_tree
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]

    def send_message(self, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": True  # Ativa o modo de streaming
        }
        
        try:
            # Faz a requisição com streaming
            response = requests.post(self.api_url, headers=headers, json=data, verify=False, stream=True)
            
            if response.status_code == 200:
                # Processa a resposta em streaming
                assistant_message = ""
                print("Assistente: ", end="", flush=True)  # Inicia a mensagem sem quebra de linha
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_str = chunk.decode("utf-8")
                        if chunk_str.startswith("data: "):
                            chunk_data = chunk_str[6:]  # Remove o prefixo "data: "
                            if chunk_data.strip() == "[DONE]":
                                break  # Fim do streaming
                            try:
                                chunk_json = json.loads(chunk_data)
                                content = chunk_json["choices"][0]["delta"].get("content", "")
                                assistant_message += content
                                print(content, end="", flush=True)  # Imprime o conteúdo em tempo real
                            except json.JSONDecodeError:
                                print("\nErro ao decodificar JSON.", flush=True)
                                return None
                print()  # Quebra de linha ao final da mensagem
                return assistant_message
            else:
                print(f"Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return None

    def carregar_sub_arvore(self, arquivo):
        """Carrega uma sub-árvore de decisões a partir de um arquivo JSON."""
        try:
            with open(arquivo, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Arquivo de sub-árvore não encontrado: {arquivo}")
            return None
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON: {arquivo}")
            return None

    def get_response_from_decision_tree(self, user_input):
        """Processa a entrada do usuário e retorna a resposta da árvore de decisões."""
        for item in self.decision_tree["NODOS"]:
            if item["pergunta"].lower() in user_input.lower():
                if item.get("proxima_acao") == "carregar_arquivo":
                    sub_arvore = self.carregar_sub_arvore(item["arquivo"])
                    if sub_arvore:
                        return sub_arvore["resposta"], sub_arvore["sugestoes"]
                else:
                    return item["resposta"], item["sugestoes"]
        return None, self.decision_tree["sugestoes_gerais"]

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
                    # Aqui, api_response já é a mensagem do assistente (string)
                    self.conversation_history.append({"role": "assistant", "content": api_response})
                else:
                    print(self.error_message)