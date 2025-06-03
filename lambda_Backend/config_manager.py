import json

class ConfigManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = self._load_config()

    def _load_config(self):
        """Carrega as configurações do arquivo JSON."""
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Erro ao decodificar o arquivo JSON: {self.config_file_path}")

    def get_config(self):
        """Retorna as configurações carregadas."""
        return self.config