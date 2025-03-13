import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from fuzzywuzzy import process

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
        self.sub_arvores_carregadas = []  # Lista para armazenar subárvores carregadas

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
        """Carrega a subárvore de decisão a partir de um arquivo JSON."""
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                sub_arvore = json.load(f)
                self.sub_arvores_carregadas.append(sub_arvore)  # Armazena a subárvore carregada
                return sub_arvore
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo} não encontrado.")
            return None
        except json.JSONDecodeError:
            print(f"Erro: Arquivo {arquivo} está mal formatado.")
            return None

    def encontrar_pergunta_mais_similar(self, user_input, perguntas):
        """Encontra a pergunta mais similar usando fuzzywuzzy."""
        pergunta_similar, score = process.extractOne(user_input, perguntas)
        
        # Define um limite de similaridade (por exemplo, 70)
        if score > 75:
            return pergunta_similar
        else:
            return None
        
    def buscar_respostas(self, user_input):
        """Busca a resposta no decision_tree principal e nas subárvores carregadas."""
        
        # 1. Primeiro, verifica perguntas relacionadas
        resposta_relacionada = self.verificar_perguntas_relacionadas(user_input)
        if resposta_relacionada:
            return resposta_relacionada, []

        # 2. Se não encontrou em perguntas relacionadas, busca no decision_tree principal
        resposta, sugestoes = self.get_response_from_decision_tree(user_input)
        if resposta:
            return resposta, sugestoes

        # 3. Se ainda não encontrou, retorna None
        return None, []



    def get_response_from_decision_tree(self, user_input):
        """Processa a entrada do usuário e retorna a resposta e sugestões da subárvore correspondente."""
        pergunta_similar = self.encontrar_pergunta_mais_similar(user_input, [item["pergunta"] for item in self.decision_tree["NODOS"]])
        
        if pergunta_similar:
            for item in self.decision_tree["NODOS"]:
                if item["pergunta"] == pergunta_similar:
                    if item.get("proxima_acao") == "carregar_arquivo":
                        sub_arvore = self.carregar_sub_arvore(item["arquivo"])
                        if sub_arvore:
                            # Retorna a resposta e sugestões da subárvore
                            return sub_arvore.get("resposta"), sub_arvore.get("sugestoes", [])
                        else:
                            return None, []
                    else:
                        return item.get("resposta"), item.get("sugestoes", [])
        
        return None, []

    def verificar_perguntas_relacionadas(self, user_input):
        """Verifica se a pergunta do usuário é similar a alguma pergunta relacionada nos NODOS principais ou nas subárvores carregadas."""
        
        # 1. Verifica no próprio decision_tree principal
        for nodo in self.decision_tree["NODOS"]:
            if "perguntas_relacionadas" in nodo:
                perguntas = [p["pergunta"] for p in nodo["perguntas_relacionadas"]]
                pergunta_similar = self.encontrar_pergunta_mais_similar(user_input, perguntas)

                if pergunta_similar:
                    for p in nodo["perguntas_relacionadas"]:
                        if p["pergunta"] == pergunta_similar:
                            # Responde e resetar o fluxo de subárvore se necessário
                            self.sub_arvores_carregadas = []  # Reseta subárvores carregadas
                            return p["resposta"]

        # 2. Verifica nas subárvores carregadas
        for sub_arvore in self.sub_arvores_carregadas:
            if "perguntas_relacionadas" in sub_arvore:
                perguntas = [p["pergunta"] for p in sub_arvore["perguntas_relacionadas"]]
                pergunta_similar = self.encontrar_pergunta_mais_similar(user_input, perguntas)

                if pergunta_similar:
                    for p in sub_arvore["perguntas_relacionadas"]:
                        if p["pergunta"] == pergunta_similar:
                            # Responde e resetar o fluxo de subárvore se necessário
                            self.sub_arvores_carregadas = []  # Reseta subárvores carregadas
                            return p["resposta"]

        return None  # Nenhuma resposta encontrada


    def start_conversation(self):
        print(self.welcome_message)

        while True:
            user_input = input("Você: ")

            if user_input.upper() == self.exit_command:
                print(self.goodbye_message)
                break

            self.conversation_history.append({"role": "user", "content": user_input})

            # Busca a resposta
            resposta, sugestoes = self.buscar_respostas(user_input)

            if resposta:
                print(f"Assistente: {resposta}")

                # Exibe sugestões, se houver
                if sugestoes:
                    print(f"[SUGESTÕES: {', '.join(sugestoes)}]")

                self.conversation_history.append({"role": "assistant", "content": resposta})
            else:
                # Se nenhuma resposta for encontrada, usa a API
                api_response = self.send_message(self.conversation_history)
                if api_response:
                    self.conversation_history.append({"role": "assistant", "content": api_response})
                else:
                    print(self.error_message)
