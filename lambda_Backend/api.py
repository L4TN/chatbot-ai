# api.py
from flask import Flask, request, jsonify
from chatbot import Chatbot
from config_manager import ConfigManager
import threading
import requests

app = Flask(__name__)

# Configurações
config_manager = ConfigManager("config.json")
config = config_manager.get_config()

# Substitui placeholders pelos valores reais (igual ao main.py)
system_prompt = config["SYSTEM_PROMPT"].format(
    BUSINESS_TYPE=config["BUSINESS_TYPE"],
    BUSINESS_DETAILS=config["BUSINESS_DETAILS"],
    CHATBOT_FOCUS=config["CHATBOT_FOCUS"]
)
welcome_message = config["WELCOME_MESSAGE"].format(
    BUSINESS_TYPE=config["BUSINESS_TYPE"],
    BUSINESS_DETAILS=config["BUSINESS_DETAILS"],
    CHATBOT_FOCUS=config["CHATBOT_FOCUS"]
)

# Inicializa o Chatbot
chatbot = Chatbot(
    api_key=config["API_KEY"],
    api_url=config["API_URL"],
    system_prompt=system_prompt,
    exit_command=config["EXIT_COMMAND"],
    welcome_message=welcome_message,
    goodbye_message=config["GOODBYE_MESSAGE"],
    error_message=config["ERROR_MESSAGE"],
    decision_tree=config["DECISION_TREE"]
)

@app.route('/receive-message', methods=['POST'])
def handle_message():
    data = request.json
    number = data['number']
    message = data['message']
    
    # Processa a mensagem em uma thread separada
    threading.Thread(target=process_message, args=(number, message)).start()
    
    return jsonify({"status": "processing"})

def process_message(number, message):
    try:
        # Obter resposta do chatbot
        response = chatbot.get_response(message)
        
        # Enviar resposta para o Node.js
        requests.post(
            'http://localhost:3000/send-message',
            json={'number': number, 'message': response},
            timeout=10
        )
    except Exception as e:
        print(f"Error processing message: {e}")
        # Send error message
        try:
            requests.post(
                'http://localhost:3000/send-message',
                json={'number': number, 'message': config["ERROR_MESSAGE"]},
                timeout=10
            )
        except:
            pass

if __name__ == '__main__':
    app.run(port=5000)
