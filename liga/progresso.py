# -*- coding: utf-8 -*-
"""O seu placar na trilha:  make progresso  ou  progresso()"""
from liga import contrato
from liga.banco import C, F, N, V, A, valor
from liga.conferir import conferiu

ETAPAS = [
    (1, "Conhecer o DW", None),
    (2, "O notebook herdado", "legado"),
    (3, "Feature table do cliente", "fs_cliente"),
    (4, "Tabela de treino do antifraude", "ds_pedido_fraude"),
    (5, "Painel cliente × mês", "ds_cliente_mes"),
    (6, "Série temporal do peso", "ds_peso_dia"),
    (7, "Rótulo por regra: entregas", "ds_entrega"),
]


def progresso():
    feitas = 0
    print()
    print("%sO seu placar%s" % (N, F))
    print()
    for n, nome, alvo in ETAPAS:
        if alvo is None:
            estado, ok = "%s(leitura)%s" % (C, F), None
        elif alvo == "legado":
            ok = bool(valor("SELECT to_regclass('legado.dataset_fraude') IS NOT NULL"))
            estado = "%s✅ investigado%s" % (V, F) if ok else "%s⏳ falta rodar o notebook%s" % (A, F)
        else:
            existe = bool(valor("SELECT to_regclass('analytics.%s') IS NOT NULL" % alvo))
            ok = existe and conferiu(alvo)
            if ok:
                estado = "%s✅ analytics.%s conferida%s" % (V, alvo, F)
            elif existe:
                estado = "%s⚠️  analytics.%s com pendências: make conferir t=%s%s" % (A, alvo, alvo, F)
            else:
                estado = "%s⏳ a fazer%s" % (C, F)
        if ok:
            feitas += 1
        print("  Etapa %d  %-34s %s" % (n, nome, estado))
    total = len([e for e in ETAPAS if e[2]])
    barra = "█" * feitas + "░" * (total - feitas)
    print()
    print("  %s  %d de %d etapas com prova concluídas" % (barra, feitas, total))
    if feitas == total:
        print("  %s🏁 Trilha completa. Siga para os desafios: desafios/desafios.md%s" % (V, F))
    print()


if __name__ == "__main__":
    progresso()
