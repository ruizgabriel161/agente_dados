from typing import override
from app.config.config_env import Settings
from app.graph.nodes.base_node import BaseNode
from langchain.messages import HumanMessage, AIMessage, SystemMessage


from app.graph.prompts.prompt import Supervisor
from app.graph.states.state import State
from rich import print
from rich.markdown import Markdown
from app.graph.tools.sql_tool import SQLBot

import re


class GerarSQLNode(BaseNode):
    """
    Classe responsável por gerar o sql
    """

    def __init__(self, llm):
        super().__init__(llm)

    @override
    def node_process(self, state: State) -> State:
        # ultima Humam message
        human_message: str = str(
            [m.content for m in state["messages"] if isinstance(m, HumanMessage)][-1]
        )

        sqlbot = SQLBot()
        schema = sqlbot.ensure_table(name="GC_RPAO", path="data/raw/teste.xlsx")

        prompt: str = Supervisor(agent="sql").defined_prompt(
            question=human_message, schema=schema
        )

        temperature = 0
        llm = self.llm.with_config(
            config={"configurable": {"temperature": temperature, 'model': Settings().MODEL_CODE}}
        )


        llm_response: AIMessage = llm.invoke(
            [SystemMessage(prompt), HumanMessage(human_message)]
        )

        model_name = llm_response.response_metadata.get('model', '')

        query: str = str(llm_response.content).strip().replace("\n", "")
        query = self.extract_sql(text=query)

        print(f"[blue]Etapa de execução: >GerarSQLNode ({model_name})")

        print(f"Mensagem: {human_message}\nQuery: {query}")
        print(Markdown("---"))

        tool_message = AIMessage(
            content="",
            tool_calls=[{"id": "sql-1", "name": "query", "args": {"query": query}}],
        )

        return {
            "messages": list(state["messages"]) + [tool_message],
            "sql_executed": True,
        }

    @override
    def name(self) -> str:
        return "gerar_sql_node"

    def extract_sql(self, text: str) -> str:

        sql_keywords = [
            "SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
            "JOIN", "ON", "GROUP BY", "ORDER BY", "HAVING", "LIMIT",
            "AND", "OR", "AS"
        ]

        text = text.strip()
        text = re.sub(r"```(?:sql)?", "", text, flags=re.IGNORECASE)
        text = text.replace("```", "")

        # 2. Extrai a query
        match = re.search(r"(SELECT[\s\S]+?;)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"(SELECT[\s\S]+)", text, re.IGNORECASE)

        if not match:
            raise ValueError("Nenhuma query SQL válida encontrada")

        sql = match.group(1).strip()

        # 3. Protege strings ('...')
        strings = {}
        def _protect(match):
            key = f"__STR_{len(strings)}__"
            strings[key] = match.group(0)
            return key

        sql = re.sub(r"'[^']*'", _protect, sql)

        # 4. Corrige palavras-chave coladas
        for kw in sorted(sql_keywords, key=len, reverse=True):
            pattern = rf"(?i)(?<!\w){kw}(?!\w)"
            sql = re.sub(pattern, f" {kw.upper()} ", sql)

        # 5. Corrige casos tipo: RemuneracaoFROM, GC_RPAOWHERE
        for kw in ["FROM", "WHERE", "JOIN", "ON", "GROUP", "ORDER", "LIMIT"]:
            sql = re.sub(rf"(?i)(\w)({kw})", r"\1 \2", sql)
            sql = re.sub(rf"(?i)({kw})(\w)", r"\1 \2", sql)

        # 6. Restaura strings
        for key, value in strings.items():
            sql = sql.replace(key, value)

        # 7. Normaliza espaços
        sql = re.sub(r"\s+", " ", sql).strip()

        # 8. Validação mínima
        if not sql.upper().startswith("SELECT"):
            raise ValueError("SQL inválido: apenas SELECT permitido")

        return sql