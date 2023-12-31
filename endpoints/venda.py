from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

venda_bp = Blueprint('venda', __name__)
conexao = Conexao()

@venda_bp.route('/vendas', methods=['GET'])
@verifica_token
def obter_vendas(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda'):
        return jsonify({'message': 'Usuário não possui acesso a consulta de Venda'}), 403
    
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
@verifica_token
def obter_venda(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda'):
        return jsonify({'message': 'Usuário não possui acesso a consulta de Venda'}), 403
    
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
    
@venda_bp.route('/vendas_itens', methods=['GET'])
@verifica_token
def obter_venda_item(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_item'):
       id_usuario = '' 
    
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

        if id_usuario:
            conditions.append("and c.id_usuario = %s")

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
                       vp.forma_pagamento,
                       vp.status as status_pagamento,
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
                  left join venda_pagamento vp on vp.id_venda = v.id_venda
                 where 1=1 {where_clause}
                 order by 1, 2 desc, 3
                """

        # Parâmetros a serem passados na consulta
        params = [tipo, id_venda, id_cliente, data, id_usuario]

        # Remove None da lista de parâmetros para os que não foram fornecidos
        params = [param for param in params if param is not None]

        # Executa a consulta SQL
        resultado = conexao.execute_query(query, params)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            vendas_itens = [dict(zip(colunas, vendas_itens)) for vendas_itens in resultado]
            return jsonify(vendas_itens)
        else:
            return jsonify({'message': 'Item de Venda não encontrado'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter itens das vendas: {str(e)}")
        return jsonify({'message': 'Erro ao obter item das vendas'}), 500
    
@venda_bp.route('/vendas', methods=['POST'])
@verifica_token
def inserir_venda(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Venda'}), 403
    
    try:
        dados_venda = request.get_json()

        query = """
                    INSERT INTO venda (id_cliente, id_funcionario, data, valor_total_venda)
                    VALUES (%s, null, now(), %s)
                """

        params = (
            dados_venda['id_cliente'],
            dados_venda['valor_total_venda']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda inserida com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir venda: {str(e)}")
        return jsonify({'message': 'Erro ao inserir venda'}), 500

@venda_bp.route('/vendas/<int:id_venda>', methods=['PUT'])
@verifica_token
def atualizar_venda(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Venda'}), 403
    
    try:
        dados_venda = request.get_json()

        query = """
                    UPDATE venda
                    SET id_cliente = %s, 
                        id_funcionario = %s, 
                        data = %s,
                        valor_total_venda = %s
                    WHERE id_venda = %s
                """

        params = (
            dados_venda['id_cliente'],
            dados_venda['id_funcionario'],
            dados_venda['data'],
            dados_venda['valor_total_venda'],
            id_venda
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda atualizada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar venda: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar venda'}), 500

@venda_bp.route('/vendas/<int:id_venda>', methods=['DELETE'])
@verifica_token
def deletar_venda(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Venda'}), 403
    
    try:
        query = "DELETE FROM venda WHERE id_venda = %s"
        params = (id_venda,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda deletada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao excluir venda: {str(e)}")
        return jsonify({'message': 'Erro ao excluir venda'}), 500

@venda_bp.route('/vendas_itens', methods=['POST'])
@verifica_token
def inserir_venda_item(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_item'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Item de Venda'}), 403
    
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
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao inserir item da venda'}), 500

@venda_bp.route('/vendas_itens/<int:id_venda>/<int:item>', methods=['PUT'])
@verifica_token
def atualizar_venda_item(payload, id_venda, item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_item'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Item de Venda'}), 403
    
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
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar item da venda'}), 500

@venda_bp.route('/vendas_itens/<int:id_venda>/<int:item>', methods=['DELETE'])
@verifica_token
def deletar_venda_item(payload, id_venda, item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_item'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Item de Venda'}), 403
    
    try:
        query = "DELETE FROM venda_item WHERE id_venda = %s AND item = %s"
        params = (id_venda, item)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de venda deletado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao excluir item da venda: {str(e)}")
        return jsonify({'message': 'Erro ao excluir item da venda'}), 500
