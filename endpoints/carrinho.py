from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso
from datetime import datetime

carrinho_bp = Blueprint('carrinho', __name__)

conexao = Conexao()

@carrinho_bp.route('/carrinhos/<int:id_cliente>', methods=['GET'])
@verifica_token
def obter_carrinhos_cliente(payload, id_cliente):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
       id_usuario = '' 
    
    try:
        if id_usuario:
            query = f'''
                    select c.id_cliente,
                           c2.nome,
                           c.id_item,
                           i.descricao,
                           i.unid_medida,
                           c.quantidade,
                           c.data_atualizacao,
                           c.valor_unitario,
                           c.valor_desconto,
                           c.valor_total_item
                      from carrinho c 
                      join cliente c2 on c2.id_cliente  = c.id_cliente 
                      join item i on i.id_item = c.id_item
                     where c.id_cliente = %s
                       and c2.id_usuario = '{id_usuario}'
                '''
        else:
            query = '''
                    select c.id_cliente,
                           c2.nome,
                           c.id_item,
                           i.descricao,
                           i.unid_medida,
                           c.quantidade,
                           c.data_atualizacao,
                           c.valor_unitario,
                           c.valor_desconto,
                           c.valor_total_item
                      from carrinho c 
                      join cliente c2 on c2.id_cliente  = c.id_cliente 
                      join item i on i.id_item = c.id_item
                     where c.id_cliente = %s
                '''
        resultado = conexao.execute_query(query, (id_cliente,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            carrinhos = [dict(zip(colunas, carrinho)) for carrinho in resultado]
            return jsonify(carrinhos)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter carrinhos: {str(e)}")
        return jsonify({'message': 'Erro ao obter carrinhos'}), 500

@carrinho_bp.route('/carrinhos', methods=['POST'])
@verifica_token
def inserir_carrinho(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Carrinho'}), 403
    
    try:
        dados_carrinho = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.carrinho (id_cliente, id_item, quantidade, data_atualizacao, valor_unitario, valor_desconto, valor_total_item)
                VALUES (%s, %s, %s, now(), %s, %s, %s)
                """

        params = (
            dados_carrinho['id_cliente'],
            dados_carrinho['id_item'],
            dados_carrinho['quantidade'],
            dados_carrinho['valor_unitario'],
            dados_carrinho['valor_desconto'],
            dados_carrinho['valor_total_item'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho inserido com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao inserir carrinho'}), 500

@carrinho_bp.route('/carrinhos/<int:id_cliente>/<int:id_item>', methods=['PUT'])
@verifica_token
def atualizar_carrinho(payload, id_cliente, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Carrinho'}), 403
    
    try:
        dados_carrinho = request.get_json()

        query = """
                UPDATE db_coffeeshop.carrinho
                SET quantidade = %s, 
                    data_atualizacao = now(),
                    valor_total_item = %s * (valor_unitario - valor_desconto)
                WHERE id_cliente = %s AND id_item = %s
                """

        params = (
            dados_carrinho['quantidade'],
            dados_carrinho['quantidade'],
            id_cliente,
            id_item,
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho atualizado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar carrinho'}), 500

@carrinho_bp.route('/carrinhos/<int:id_cliente>/<int:id_item>', methods=['DELETE'])
@verifica_token
def deletar_carrinho(payload, id_cliente, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Carrinho'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.carrinho WHERE id_cliente = %s AND id_item = %s"
        params = (id_cliente, id_item)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho deletado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao deletar carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao deletar carrinho'}), 500

@carrinho_bp.route('/finaliza_carrinho/<int:id_cliente>', methods=['POST'])
@verifica_token
def finaliza_carrinho(payload, id_cliente):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'finaliza_carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a finalizar carrinho'}), 403
    
    try:
        # Verificar se o carrinho está vazio
        query_carrinho_vazio = 'SELECT COUNT(*) FROM carrinho WHERE id_cliente = %s'
        resultado_carrinho_vazio = conexao.execute_query(query_carrinho_vazio, (id_cliente,))
        if resultado_carrinho_vazio and resultado_carrinho_vazio[0][0] == 0:
            return jsonify({'message': 'Carrinho está vazio'}), 400

        # Verificar se há saldo disponível para cada item no carrinho
        query_saldo_disponivel = """
            SELECT c.id_item, i.descricao
            FROM carrinho c
            JOIN item_conta_estoque ics ON c.id_item = ics.id_item
            JOIN item i ON c.id_item = i.id_item
            WHERE c.id_cliente = %s AND ics.conta_padrao = 'S' AND ics.saldo < c.quantidade
        """
        params_saldo_disponivel = (id_cliente,)
        resultado_saldo_disponivel = conexao.execute_query(query_saldo_disponivel, params_saldo_disponivel)

        if resultado_saldo_disponivel:
            mensagem = 'Saldo insuficiente para os seguintes itens:\n'
            for item in resultado_saldo_disponivel:
                mensagem += f'ID do Item: {item[0]}, Descrição: {item[1]}\n'
            return jsonify({'message': mensagem}), 400

        # Inserir venda
        data_atual = datetime.now().date()
        query_inserir_venda = """
            INSERT INTO db_coffeeshop.venda (id_cliente, data, valor_total_venda)
            SELECT %s, %s, SUM(ci.quantidade * (ci.valor_unitario - ci.valor_desconto))
            FROM carrinho ci
            WHERE ci.id_cliente = %s
        """
        params_inserir_venda = (id_cliente, data_atual, id_cliente)
        conexao.execute_query(query_inserir_venda, params_inserir_venda)
        conexao.connection.commit()

        # Obter o ID da venda recém-criada
        query_obter_id_venda = 'SELECT LAST_INSERT_ID()'
        id_venda = conexao.execute_query(query_obter_id_venda)[0][0]

        # Inserir venda_item
        query_inserir_venda_item = """
            INSERT INTO db_coffeeshop.venda_item (id_venda, item, id_item, quantidade, valor_unitario, valor_desconto, valor_total_item)
            SELECT %s, ci.id_item, ci.id_item, ci.quantidade, ci.valor_unitario, ci.valor_desconto, ci.valor_total_item
            FROM carrinho ci
            JOIN item it ON ci.id_item = it.id_item
            WHERE ci.id_cliente = %s
        """
        params_inserir_venda_item = (id_venda, id_cliente)
        conexao.execute_query(query_inserir_venda_item, params_inserir_venda_item)
        conexao.connection.commit()

        # Atualizar saldo na tabela item_conta_estoque
        query_atualizar_saldo = """
            UPDATE item_conta_estoque ics
            JOIN carrinho ci ON ics.id_item = ci.id_item
            SET ics.saldo = ics.saldo - ci.quantidade, ics.data_atualizacao = now()
            WHERE ics.conta_padrao = 'S' AND ci.id_cliente = %s
        """
        params_atualizar_saldo = (id_cliente,)
        conexao.execute_query(query_atualizar_saldo, params_atualizar_saldo)
        conexao.connection.commit()

        # Limpar carrinho
        query_limpar_carrinho = 'DELETE FROM carrinho WHERE id_cliente = %s'
        conexao.execute_query(query_limpar_carrinho, (id_cliente,))
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho finalizado com sucesso',
                        'id_venda': id_venda}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao finalizar carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao finalizar carrinho'}), 500