
from typing import cast
from app.config.config_env import Settings
from langchain.chat_models import init_chat_model, BaseChatModel

class LoadLLM():
    '''Classe responsável por carregar os modelos de LLM'''
    def __init__(self,  llm: str = Settings().MODEL, base_url:str = Settings().LLM_HOST) -> None:
        '''
        Construtor da classe LoadLLM

        Keyword Arguments:
            llm (str) -- modelo usado no projeto (default: {Settings.MODEL})
            base_url (str) -- url onde o modelo está ridando (default: {Settings.MODEL})
        '''        
        self.llm = llm
        self.base_url = base_url

    def init_llm(self) -> BaseChatModel:
        try:
            model = cast(
                'BaseChatModel',
                init_chat_model(
                    model=self.llm, 
                    base_url=self.base_url,
                    temperature=0.5,
                    configurable_fields=('temperature', 'model', )
                )
            )

            assert hasattr(model, 'bind_tools')
            assert hasattr(model, 'invoke')
            assert hasattr(model, 'with_config')
            
            return model

        except Exception as e:
            raise ValueError(f'Erro ao carregar o modelo {self.llm=}, {e}')


    



    