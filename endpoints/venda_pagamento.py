from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

venda_pagamento_bp = Blueprint('venda_pagamento', __name__)

conexao = Conexao()

@venda_pagamento_bp.route('/venda_pagamentos/<int:id_venda>', methods=['GET'])
@verifica_token
def obter_venda_pagamentos_venda(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_pagamento'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Venda Pagamento'}), 403
    
    try:
        query = 'SELECT * FROM venda_pagamento WHERE id_venda = %s'
        resultado = conexao.execute_query(query, (id_venda,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            venda_pagamentos = [dict(zip(colunas, venda_pagamento)) for venda_pagamento in resultado]
            return jsonify(venda_pagamentos)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter venda_pagamentos: {str(e)}")
        return jsonify({'message': 'Erro ao obter venda_pagamentos'}), 500


@venda_pagamento_bp.route('/venda_pagamentos', methods=['POST'])
@verifica_token
def inserir_venda_pagamento(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_pagamento'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Venda Pagamento'}), 403
    
    try:
        dados_venda_pagamento = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.venda_pagamento (id_venda, forma_pagamento, qtde_parcelas, status, data_confirmacao)
                VALUES (%s, %s, %s, %s, %s)
                """

        params = (
            dados_venda_pagamento['id_venda'],
            dados_venda_pagamento['forma_pagamento'],
            dados_venda_pagamento['qtde_parcelas'],
            dados_venda_pagamento['status'],
            dados_venda_pagamento['data_confirmacao'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda Pagamento inserido com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir venda_pagamento: {str(e)}")
        return jsonify({'message': 'Erro ao inserir venda_pagamento'}), 500

@venda_pagamento_bp.route('/venda_pagamentos/<int:id_venda>/<string:forma_pagamento>', methods=['PUT'])
@verifica_token
def atualizar_venda_pagamento(payload, id_venda, forma_pagamento):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_pagamento'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Venda Pagamento'}), 403
    
    try:
        dados_venda_pagamento = request.get_json()

        query = """
                UPDATE db_coffeeshop.venda_pagamento
                SET qtde_parcelas = %s, status = %s, data_confirmacao = %s
                WHERE id_venda = %s AND forma_pagamento = %s
                """

        params = (
            dados_venda_pagamento['qtde_parcelas'],
            dados_venda_pagamento['status'],
            dados_venda_pagamento['data_confirmacao'],
            id_venda,
            forma_pagamento,
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda Pagamento atualizado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar venda_pagamento: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar venda_pagamento'}), 500

@venda_pagamento_bp.route('/venda_pagamentos/<int:id_venda>/<string:forma_pagamento>', methods=['DELETE'])
@verifica_token
def deletar_venda_pagamento(payload, id_venda, forma_pagamento):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_pagamento'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Venda Pagamento'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.venda_pagamento WHERE id_venda = %s AND forma_pagamento = %s"
        params = (id_venda, forma_pagamento)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Venda Pagamento deletado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao deletar venda_pagamento: {str(e)}")
        return jsonify({'message': 'Erro ao deletar venda_pagamento'}), 500
