import re

def adapt_sql_for_psycopg(sql: str) -> str:
    """
    Escapa % literais para evitar conflito com placeholders do psycopg.
    Preserva %s, %b e %t.
    """
    result = []
    i = 0

    while i < len(sql):
        if sql[i] == "%":
            # placeholder válido do psycopg
            if i + 1 < len(sql) and sql[i + 1] in ("s", "b", "t"):
                result.append("%" + sql[i + 1])
                i += 1
            else:
                result.append("%%")
        else:
            result.append(sql[i])
        i += 1

    return "".join(result)

def quote_identifiers_postgres(sql: str, sql_keywords:list[str], sql_function: list[str]) -> str:
        def replacer(match):
            token = match.group(0)
            upper = token.upper()

            # ignora keywords e funções
            if upper in sql_keywords or upper in sql_function:
                return token

            # ignora números
            if token.isdigit():
                return token

            # ignora já citados
            if token.startswith('"') and token.endswith('"'):
                return token

            return f'"{token}"'

        pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        return re.sub(pattern, replacer, sql)

def extract_sql(text: str) -> str:

    sql_keywords = [
        "SELECT", "FROM", "WHERE", "INNER", "LEFT", "RIGHT",
        "JOIN", "ON", "GROUP", "BY", "ORDER", "HAVING",
        "LIMIT", "AND", "OR", "AS"
    ]

    sql_function = [
        "UPPER", "LOWER", "COUNT", "SUM", "AVG",
        "MIN", "MAX", "COALESCE"
    ]

    # 1. Limpeza inicial
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

    def _protect_string(match):
        key = f"__STR_{len(strings)}__"
        strings[key] = match.group(0)
        return key

    sql = re.sub(r"'[^']*'", _protect_string, sql)

    # 4. 🔒 Protege identificadores já citados ("...")
    quoted = {}

    def _protect_quoted(match):
        key = f"__QID_{len(quoted)}__"
        quoted[key] = match.group(0)
        return key

    sql = re.sub(r'"[^"]+"', _protect_quoted, sql)

    # 5. Corrige palavras-chave coladas
    for kw in sorted(sql_keywords, key=len, reverse=True):
        pattern = rf"(?i)(?<!\w){kw}(?!\w)"
        sql = re.sub(pattern, f" {kw.upper()} ", sql)

    # 6. Corrige casos tipo: RemuneracaoFROM, GC_RPAOWHERE
    for kw in ["FROM", "WHERE", "JOIN", "ON", "GROUP", "ORDER", "LIMIT"]:
        sql = re.sub(rf"(?i)(\w)({kw})", r"\1 \2", sql)
        sql = re.sub(rf"(?i)({kw})(\w)", r"\1 \2", sql)

    # 7. Quote automático de identificadores
    sql = quote_identifiers_postgres(
        sql,
        sql_keywords=sql_keywords,
        sql_function=sql_function
    )

    # 8. Restaura identificadores citados
    for key, value in quoted.items():
        sql = sql.replace(key, value)

    # 9. Restaura strings
    for key, value in strings.items():
        sql = sql.replace(key, value)

    # 10. Normaliza espaços
    sql = re.sub(r"\s+", " ", sql).strip()

    # 11. Corrige escapes inválidos
    sql = sql.replace("\\'", "'").replace('\\"', '"')

    # 12. Validação mínima
    if not sql.upper().startswith("SELECT"):
        raise ValueError("SQL inválido: apenas SELECT permitido")

    return sql

if __name__ == "__main__":
    query = 'SELECT "Remuneracao" FROM ""dados"".""tb_colaboradores"" WHERE UPPER(""Nome_Completo"") = "\'FREDERICO DUQUE\nMARCONDES\'";'
    print(query)
    query: str = str(query ).strip().replace("\n", "")
    print(query)
    query = adapt_sql_for_psycopg(sql=query)
    print(query)
    query = extract_sql(text=query)
    print(query)
