from flask import Blueprint, jsonify, request
from conexao_db import Conexao

venda_bp = Blueprint('venda', __name__)

conexao = Conexao()

@venda_bp.route('/vendas', methods=['GET'])
def obter_vendas():
    query = 'SELECT * FROM venda'
    resultado = conexao.execute_query(query)

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        vendas = [dict(zip(colunas, venda)) for venda in resultado]
        return jsonify(vendas)
    else:
        return jsonify([])  # Retorna uma lista vazia se não houver vendas

@venda_bp.route('/vendas/<int:id_venda>', methods=['GET'])
def obter_venda(id_venda):
    query = 'SELECT * FROM venda WHERE id_venda = %s'
    resultado = conexao.execute_query(query, (id_venda,))

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        venda = dict(zip(colunas, resultado[0]))
        return jsonify(venda)
    else:
        return jsonify({'message': 'Venda não encontrada'}), 404

@venda_bp.route('/vendas_item', methods=['GET'])
def obter_venda_item():
    tipo     = request.args.get('tipo') 
    id_venda = request.args.get('id_venda')  

    query = """
            select case when vi.id_item is not null then 'Produto' else 'Assinatura' end as tipo, 
                    v.id_venda,
                    vi.item,
                    coalesce(vi.id_item, vi.id_assinatura) as id_item,
                    coalesce(i.descricao, a.descricao) as descricao,
                    v.id_cliente,
                    c.nome as nome_cliente,
                    v.id_funcionario,
                    f.nome,
                    v.data,
                    v.valor_total_venda,
                    v.forma_pagamento,
                    v.status_pagamento,
                    vi.quantidade,
                    vi.valor_unitario,
                    vi.valor_desconto,
                    vi.valor_total_item
                from venda v
                join venda_item vi on v.id_venda = vi.id_venda
                join cliente c on v.id_cliente = c.id_cliente
                left join funcionario f on v.id_funcionario = f.id_funcionario
                left join item i on vi.id_item  = i.id_item
                left join assinatura a on vi.id_assinatura = a.id_assinatura 
                where case when vi.id_item is not null then 'Produto' else 'Assinatura' end = %s
                  and v.id_venda = %s
            """
    resultado = conexao.execute_query(query, (tipo, id_venda))

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        venda = dict(zip(colunas, resultado[0]))
        return jsonify(venda)
    else:
        return jsonify({'message': 'Venda não encontrada'}), 404
