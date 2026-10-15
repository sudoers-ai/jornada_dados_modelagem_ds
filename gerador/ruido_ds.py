# -*- coding: utf-8 -*-
"""
Ruido realista: o que este repositorio acrescenta ao universo canonico.

No gerador canonico a fraude e plantada por regra: toda compra de fora de
SP, MG e RJ e fraude, toda troca de aparelho e fraude. Otimo para ensinar
modelagem dimensional; pessimo para ciencia de dados - um `if` acerta tudo
e nao sobra nada para um modelo aprender.

Aqui o mundo fica mais parecido com o de verdade:

  1. clientes legitimos VIAJAM e compram de fora da area atendida;
  2. clientes legitimos TROCAM DE CELULAR;
  3. existe um quarto tipo de fraude, o CARTAO CLONADO, que nao deixa rastro
     de aparelho nem de lugar: so um valor fora do padrao, de madrugada,
     no cartao de credito;
  4. parte das fraudes NUNCA e descoberta (o rotulo tem ruido).

Os ids (pessoa 1, pedido 1...) continuam os mesmos dos outros repositorios.
Muda so o comportamento de alguns pedidos. Tudo deterministico.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from gerador.liga_sudoers_gen import (MODELOS_DISPOSITIVO, UF_SUSPEITAS, _device_id,
                                      _geo_da_uf)

TAXA_VIAGEM = 0.012                # compras legitimas feitas de fora da area
TAXA_TROCA_CELULAR = 0.25          # pessoas que trocam de celular no periodo
TAXA_CARTAO_CLONADO = 0.20         # entre os pedidos-alvo (valor alto), quantos viram fraude
TAXA_MADRUGADA_CLONADO = 0.70      # cartao clonado costuma ser usado de madrugada
TAXA_FRAUDE_NAO_DESCOBERTA = 0.10  # fraudes que ninguem confirma (ruido no rotulo)


def aplicar_ruido(u) -> dict:
    """Altera u.pedidos no lugar. Devolve um resumo do que foi feito."""
    rnd = random.Random(u.semente * 1000 + 99)
    feito = {"viagens": 0, "trocas_de_celular": 0, "cartao_clonado": 0, "nao_descobertas": 0}

    # ------------------------------------------- 1) troca de celular legitima
    inicio = min(datetime.fromisoformat(p["dt_venda"]) for p in u.pedidos)
    fim = max(datetime.fromisoformat(p["dt_venda"]) for p in u.pedidos)
    troca = {}
    for pessoa in u.pessoas:
        if rnd.random() < TAXA_TROCA_CELULAR:
            quando = inicio + (fim - inicio) * rnd.random()
            modelo = rnd.choice([m for m in MODELOS_DISPOSITIVO if m != pessoa["dispositivo_padrao"]])
            troca[pessoa["id"]] = (quando, _device_id(rnd), modelo, pessoa["device_id"])
    for ped in u.pedidos:
        t = troca.get(ped["id_pessoa"])
        a = ped["auditoria"]
        # so os pedidos "normais" (com o aparelho de sempre) passam a usar o novo
        if t and not ped["fraude"] and a["device_id"] == t[3] \
                and datetime.fromisoformat(ped["dt_venda"]) >= t[0]:
            a["device_id"], a["dispositivo"] = t[1], t[2]
            feito["trocas_de_celular"] += 1

    # ------------------------------------------------ 2) viagem legitima
    for ped in u.pedidos:
        if not ped["fraude"] and rnd.random() < TAXA_VIAGEM:
            uf = rnd.choice(UF_SUSPEITAS)
            gh, lat, lon = _geo_da_uf(uf, rnd)
            ped["auditoria"].update({"uf": uf, "geohash": gh, "lat": lat, "lon": lon})
            feito["viagens"] += 1

    # ---------------------------------------------- 3) cartao clonado
    # alvo: pedidos legitimos bem acima do que o cliente costuma gastar
    soma, qtd = {}, {}
    for ped in u.pedidos:
        soma[ped["id_pessoa"]] = soma.get(ped["id_pessoa"], 0) + ped["valor_total"]
        qtd[ped["id_pessoa"]] = qtd.get(ped["id_pessoa"], 0) + 1
    for ped in u.pedidos:
        media = soma[ped["id_pessoa"]] / qtd[ped["id_pessoa"]]
        if not ped["fraude"] and ped["valor_total"] > 1.5 * media and rnd.random() < TAXA_CARTAO_CLONADO:
            ped["fraude"], ped["motivo_fraude"] = True, "cartao_clonado"
            if rnd.random() < TAXA_MADRUGADA_CLONADO:
                dt = datetime.fromisoformat(ped["dt_venda"])
                dt = dt.replace(hour=rnd.randint(0, 4), minute=rnd.randint(0, 59), second=rnd.randint(0, 59))
                ped["dt_venda"] = dt.isoformat()
            feito["cartao_clonado"] += 1

    # ------------------------------------- 4) fraude que ninguem descobre
    for ped in u.pedidos:
        if ped["fraude"] and rnd.random() < TAXA_FRAUDE_NAO_DESCOBERTA:
            ped["fraude"], ped["motivo_fraude"] = False, None
            feito["nao_descobertas"] += 1

    u.pedidos.sort(key=lambda p: p["dt_venda"])
    return feito
