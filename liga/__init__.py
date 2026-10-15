# -*- coding: utf-8 -*-
"""
Ferramentas da disciplina. Nos notebooks:

    from liga import sql, executar, conferir, avaliar, progresso

    sql("SELECT ...")          -> um DataFrame com o resultado
    executar("CREATE ...")     -> roda comandos (CREATE TABLE, DROP...)
    conferir("fs_cliente")     -> compara a SUA tabela com o modelo
    avaliar("fraude")          -> treina um modelo e compara notebook x producao
    progresso()                -> o seu placar na trilha
"""
from liga.banco import executar, sql          # noqa: F401
from liga.conferir import conferir            # noqa: F401
from liga.avaliar import avaliar              # noqa: F401
from liga.progresso import progresso          # noqa: F401
