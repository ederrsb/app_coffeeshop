from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

dados_entrega_bp = Blueprint('dados_entrega', __name__)

conexao = Conexao()

@dados_entrega_bp.route('/dados_entrega/<int:id_venda>', methods=['GET'])
@verifica_token
def obter_dados_entrega(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_entrega'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Dados de Entrega'}), 403
    
    try:
        query = 'SELECT * FROM venda_entrega WHERE id_venda = %s'
        resultado = conexao.execute_query(query, (id_venda,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            dados_entrega = [dict(zip(colunas, dado)) for dado in resultado]
            return jsonify(dados_entrega)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter dados de entrega: {str(e)}")
        return jsonify({'message': 'Erro ao obter dados de entrega'}), 500

@dados_entrega_bp.route('/dados_entrega', methods=['POST'])
@verifica_token
def inserir_dados_entrega(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_entrega'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Dados de Entrega'}), 403
    
    try:
        dados_entrega = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.venda_entrega (id_venda, id_cliente, seq, previsao_entrega, observacao, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_entrega['id_venda'],
            dados_entrega['id_cliente'],
            dados_entrega['seq'],
            dados_entrega['previsao_entrega'],
            dados_entrega.get('observacao', None),
            dados_entrega['status'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Dados de Entrega inseridos com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir dados de entrega: {str(e)}")
        return jsonify({'message': 'Erro ao inserir dados de entrega'}), 500

@dados_entrega_bp.route('/dados_entrega/<int:id_venda>', methods=['PUT'])
@verifica_token
def atualizar_dados_entrega(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_entrega'):
        return jsonify({'message': 'Usuário não possui acesso a atualizar Dados de Entrega'}), 403
    
    try:
        dados_entrega = request.get_json()

        query = """
                UPDATE db_coffeeshop.venda_entrega
                SET id_cliente = %s, seq = %s, previsao_entrega = %s, observacao = %s, status = %s
                WHERE id_venda = %s
                """

        params = (
            dados_entrega['id_cliente'],
            dados_entrega['seq'],
            dados_entrega['previsao_entrega'],
            dados_entrega.get('observacao', None),
            dados_entrega['status'],
            id_venda,
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Dados de Entrega atualizados com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar dados de entrega: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar dados de entrega'}), 500

@dados_entrega_bp.route('/dados_entrega/<int:id_venda>', methods=['DELETE'])
@verifica_token
def deletar_dados_entrega(payload, id_venda):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'venda_entrega'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Dados de Entrega'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.venda_entrega WHERE id_venda = %s"
        params = (id_venda,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Dados de Entrega excluídos com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao excluir dados de entrega: {str(e)}")
        return jsonify({'message': 'Erro ao excluir dados de entrega'}), 500
