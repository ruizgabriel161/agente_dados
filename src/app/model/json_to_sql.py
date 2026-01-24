from typing import Any, Dict, List, Tuple
from psycopg import sql

class JsonToSQL():
    """
    Classe Responsável por converter o json gerado pela LLM em SQL
    """
    ALLOWED_OPERATORS = ["=", ">", "<", ">=", "<=", "LIKE"]
    ALLOWED_FUNCTIONS = ["UPPER", "LOWER"]

    def __init__(self, payload:Dict[str,Any]):

        self.json:Dict[str,Any] = self._validade_json(json=payload)

    def _validade_json(self, json:Dict[str,Any]) -> Dict[str,Any]:
        '''
        _validade_json Função para validar o json passado para o método

        Args:
            json (Dict[str,Any]): json com o mapeamento de dados

        Raises:
            ValueError: Json incompleto
            ValueError: Erro caso o campo columns não for uma lista ou não foi passado no json
            ValueError: Erro se alguma coluna não for string
            ValueError: Erro se o schema não for string
            ValueError: Erro se a tabela não for uma string
            ValueError: Erro se o operador do where não estiver na constante ALLOWED_OPERATORS
            ValueError: Erro se a função não estiver na constante ALLOWED_OPERATORS

        Returns:
            Dict[str,Any]: Retorno do Json
        '''        
        required_keys = {"schema", "table", "columns"}

        if not required_keys.issubset(json):
            raise ValueError("json incompleto")
        
        if "." in json["schema"]:
            raise ValueError("schema não pode conter '.'")

        if "." in json["table"]:
            raise ValueError("table não pode conter '.'")

        if not isinstance(json["columns"], list) or not json["columns"]:
            raise ValueError("columns deve ser uma lista não vazia")

        for col in json["columns"]:
            if not isinstance(col, str):
                raise ValueError("Nome de coluna inválido")

        if not isinstance(json["schema"], str):
            raise ValueError("schema inválido")

        if not isinstance(json["table"], str):
            raise ValueError("table inválido")

        for w in json.get("where", []):
            if w["operator"] not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operador inválido: {w['operator']}")

            if w.get("function") and w["function"] not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"Função inválida: {w['function']}")
        return json

    def build_select(self) -> Tuple[sql.Composed, List[Any]]:
        '''
        build_select Cria o select a partir do json

        Returns:
            Tuple[sql.Composed, List[Any]]: Devolve a query e o parametro
        '''        
        # SELECT columns
        columns_sql = sql.SQL(", ").join(
            sql.Identifier(col) for col in self.json["columns"]
        )

        # schema.table
        table_sql = sql.SQL(".").join([
            sql.Identifier(self.json["schema"]),
            sql.Identifier(self.json["table"])
        ])

        where_clauses = []
        params: List[Any] = []

        for w in self.json.get("where", []):
            column_sql = sql.Identifier(w["column"])

            # Função (ex: UPPER(col))
            if w.get("function"):
                column_sql = sql.SQL("{}({})").format(
                    sql.SQL(w["function"]),
                    column_sql
                )

            where_clauses.append(
                sql.SQL("{} {} %s").format(
                    column_sql,
                    sql.SQL(w["operator"])
                )
            )

            params.append(w["value"])

        query = sql.SQL("SELECT {} FROM {}").format(
            columns_sql,
            table_sql
        )

        if where_clauses:
            query = sql.SQL(" ").join([
            query,
            sql.SQL("WHERE"),
            sql.SQL(" AND ").join(where_clauses)
        ])


        return query, params

