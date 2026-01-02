from pydantic_settings import BaseSettings, SettingsConfigDict 



class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file='.env',  # determina onde está armazena as variaveis de ambiente, 
        extra='allow' # permite variáveis desconhecidas
        )

    APP_NAME:str = 'agente_dados' #Nome do aplicativo
    MODEL:str = 'llama3.1'   # valores Default
    MODEL_CODE:str = ''
    LLM_HOST:str = 'http://localhost:11434' #localhost da llm
    DATA_DSN: str = ''


if __name__ == '__main__':
    Settings()



