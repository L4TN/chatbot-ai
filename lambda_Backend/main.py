from config_manager import ConfigManager
from chatbot import Chatbot

def main():
    # Carrega as configurações
    config_manager = ConfigManager("config.json")
    config = config_manager.get_config()

    # Substitui placeholders pelos valores reais
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

    # Injeção de dependências
    chatbot = Chatbot(
        api_key=config["API_KEY"],
        api_url=config["API_URL"],
        system_prompt=system_prompt,
        exit_command=config["EXIT_COMMAND"],
        welcome_message=welcome_message,
        goodbye_message=config["GOODBYE_MESSAGE"],
        error_message=config["ERROR_MESSAGE"],
        decision_tree=config["DECISION_TREE"],
        rag_catalog=config.get("RAG_CATALOG")
    )

    # Inicia a conversa
    chatbot.start_conversation()

if __name__ == "__main__":
    main()
