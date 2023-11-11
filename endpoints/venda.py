from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

venda_bp = Blueprint('venda', __name__)

conexao = Conexao()

@venda_bp.route('/vendas', methods=['GET'])
def obter_vendas():
    try:
        query = 'SELECT * FROM venda'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            vendas = [dict(zip(colunas, venda)) for venda in resultado]
            return jsonify(vendas)
        else:
            return jsonify([])  # Retorna uma lista vazia se não houver vendas
    except Exception as e:
        logger.error(f"Erro ao obter vendas: {str(e)}")
        return jsonify({'message': 'Erro ao obter vendas'}), 500

@venda_bp.route('/vendas/<int:id_venda>', methods=['GET'])
def obter_venda(id_venda):
    try:
        query = 'SELECT * FROM venda WHERE id_venda = %s'
        resultado = conexao.execute_query(query, (id_venda,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            venda = dict(zip(colunas, resultado[0]))
            return jsonify(venda)
        else:
            return jsonify({'message': 'Venda não encontrada'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter venda: {str(e)}")
        return jsonify({'message': 'Erro ao obter venda'}), 500
    
@venda_bp.route('/vendas_item', methods=['GET'])
def obter_venda_item():
    try:
        tipo = request.args.get('tipo')
        id_venda = request.args.get('id_venda')
        id_cliente = request.args.get('id_cliente')
        data = request.args.get('data')

        # Inicializa uma lista de condições para a cláusula WHERE
        conditions = []

        # Adiciona a condição para o parâmetro 'tipo' se ele estiver presente
        if tipo:
            conditions.append("and case when vi.id_item is not null then 'Produto' else 'Assinatura' end = %s")

        if id_venda:
            conditions.append("and v.id_venda = %s")

        if id_cliente:
            conditions.append("and v.id_cliente = %s")

        if data:
            conditions.append("and v.data = %s")

        # Constrói a cláusula WHERE combinando as condições com 'AND'
        where_clause = "".join(conditions) if conditions else ""

        # Constrói a consulta SQL com a cláusula WHERE
        query = f"""
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
                 where 1=1 {where_clause}
                 order by 1, 2, 3
                """

        # Parâmetros a serem passados na consulta
        params = [tipo, id_venda, id_cliente, data]

        # Remove None da lista de parâmetros para os que não foram fornecidos
        params = [param for param in params if param is not None]

        # Executa a consulta SQL
        resultado = conexao.execute_query(query, params)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            vendas_itens = [dict(zip(colunas, vendas_item)) for vendas_item in resultado]
            return jsonify(vendas_itens)
        else:
            return jsonify({'message': 'Item de Venda não encontrado'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter itens das vendas: {str(e)}")
        return jsonify({'message': 'Erro ao obter item das vendas'}), 500
    
@venda_bp.route('/vendas', methods=['POST'])
def inserir_venda():
    try:
        dados_venda = request.get_json()

        query = """
                    INSERT INTO venda (id_cliente, id_funcionario, data, valor_total_venda, forma_pagamento, status_pagamento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_venda['id_cliente'],
            dados_venda['id_funcionario'],
            dados_venda['data'],
            dados_venda['valor_total_venda'],
            dados_venda['forma_pagamento'],
            dados_venda['status_pagamento']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda inserida com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir venda: {str(e)}")
        return jsonify({'message': 'Erro ao inserir venda'}), 500

@venda_bp.route('/vendas/<int:id_venda>', methods=['PUT'])
def atualizar_venda(id_venda):
    try:
        dados_venda = request.get_json()

        query = """
                    UPDATE venda
                    SET id_cliente = %s, 
                        id_funcionario = %s, 
                        data = %s,
                        valor_total_venda = %s, 
                        forma_pagamento = %s, 
                        status_pagamento = %s
                    WHERE id_venda = %s
                """

        params = (
            dados_venda['id_cliente'],
            dados_venda['id_funcionario'],
            dados_venda['data'],
            dados_venda['valor_total_venda'],
            dados_venda['forma_pagamento'],
            dados_venda['status_pagamento'],
            id_venda
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda atualizada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar venda: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar venda'}), 500

@venda_bp.route('/vendas/<int:id_venda>', methods=['DELETE'])
def deletar_venda(id_venda):
    try:
        query = "DELETE FROM venda WHERE id_venda = %s"
        params = (id_venda,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda deletada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao excluir venda: {str(e)}")
        return jsonify({'message': 'Erro ao excluir venda'}), 500

@venda_bp.route('/vendas_itens', methods=['POST'])
def inserir_venda_item():
    try:
        dados_venda_item = request.get_json()

        query = """
                    INSERT INTO venda_item (id_venda, item, id_item, id_assinatura, quantidade, valor_unitario, valor_desconto, valor_total_item)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_venda_item['id_venda'],
            dados_venda_item['item'],
            dados_venda_item['id_item'],
            dados_venda_item['id_assinatura'],
            dados_venda_item['quantidade'],
            dados_venda_item['valor_unitario'],
            dados_venda_item['valor_desconto'],
            dados_venda_item['valor_total_item']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de venda inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao inserir item da venda'}), 500

@venda_bp.route('/vendas_itens/<int:id_venda>/<int:item>', methods=['PUT'])
def atualizar_venda_item(id_venda, item):
    try:
        dados_venda_item = request.get_json()

        query = """
                    UPDATE venda_item
                    SET id_item = %s,
                        id_assinatura = %s,
                        quantidade = %s,
                        valor_unitario = %s,
                        valor_desconto = %s,
                        valor_total_item = %s
                    WHERE id_venda = %s AND item = %s
                """    

        params = (
            dados_venda_item['id_item'],
            dados_venda_item['id_assinatura'],
            dados_venda_item['quantidade'],
            dados_venda_item['valor_unitario'],
            dados_venda_item['valor_desconto'],
            dados_venda_item['valor_total_item'],
            id_venda,
            item
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de venda atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar item da venda'}), 500

@venda_bp.route('/vendas_itens/<int:id_venda>/<int:item>', methods=['DELETE'])
def deletar_venda_item(id_venda, item):
    try:
        query = "DELETE FROM venda_item WHERE id_venda = %s AND item = %s"
        params = (id_venda, item)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de venda deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao excluir item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao excluir item da venda'}), 500
