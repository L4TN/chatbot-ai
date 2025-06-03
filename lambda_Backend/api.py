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

# Inicializa o Chatbot
chatbot = Chatbot(
    api_key=config["API_KEY"],
    api_url=config["API_URL"],
    system_prompt=config["SYSTEM_PROMPT"],
    exit_command=config["EXIT_COMMAND"],
    welcome_message=config["WELCOME_MESSAGE"],
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
    # Obter resposta do chatbot
    response = chatbot.get_response(message)
    
    # Enviar resposta para o Node.js
    requests.post(
        'http://localhost:3000/send-message',
        json={'number': number, 'message': response}
    )

if __name__ == '__main__':
    app.run(port=5000)