from sqlalchemy.engine import create_engine
from sqlalchemy.engine import Engine
from pandas import read_excel, DataFrame

from app.config.config_env import Settings


class ExcelToPostgress(object):
    """Classe criada para carregar o excel para o banco de dados."""

    def __init__(self, data_dsn: str):
        '''
        __init__ Inicializador da classe

        Args:
            data_dsn (str): caminho do banco de dados
        '''        
        self._engine: Engine = self._set_engine(data_dsn=data_dsn) 

    def _set_engine(self, data_dsn: str) -> Engine:
        return create_engine(data_dsn)

    def load_to_postgres(self, path: str, table: str, schema: str) -> None:
        """
        load_to_postgres Método responsável por transformar a tabela excel para postgress

        Args:
            path (str): caminho do arquivo excel
            table (str): nome da tabela no postgres
            schema (str): schema onde a tabela será salva

        Raises:
            ValueError: Exception caso o salvamento de errado
        """
        df: DataFrame = read_excel(io=path)

        try:
            df.to_sql(
                name=table,
                con=self._engine,
                schema=schema,
                if_exists="replace",
                index=False,
            )
        except Exception as e:
            raise ValueError(f"Erro ao subir o excel para o banco de dados{e}")


if __name__ == "__main__":
    ExcelToPostgress(Settings().DATA_DSN).load_to_postgres(
        path="data/raw/teste.xlsx", table="tb_colaboradores", schema="dados"
    )
