from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token

conta_estoque_bp = Blueprint('conta_estoque', __name__)
conexao = Conexao()

@conta_estoque_bp.route('/contas_estoque', methods=['GET'])
@verifica_token
def obter_contas_estoque(payload):
    try:
        query = 'SELECT * FROM conta_estoque'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            contas_estoque = [dict(zip(colunas, conta_estoque)) for conta_estoque in resultado]
            return jsonify(contas_estoque)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter contas de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao obter contas de estoque'}), 500

@conta_estoque_bp.route('/contas_estoque', methods=['POST'])
@verifica_token
def inserir_conta_estoque(payload):
    try:
        dados_conta_estoque = request.get_json()

        query = """
                    INSERT INTO conta_estoque (descricao)
                    VALUES (%s)
                """

        params = (
            dados_conta_estoque['descricao'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Conta de estoque inserida com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao inserir conta de estoque'}), 500

@conta_estoque_bp.route('/contas_estoque/<int:id_conta_estoque>', methods=['PUT'])
@verifica_token
def atualizar_conta_estoque(payload, id_conta_estoque):
    try:
        dados_conta_estoque = request.get_json()

        query = """
                    UPDATE conta_estoque
                    SET descricao = %s
                    WHERE id_conta_estoque = %s
                """

        params = (
            dados_conta_estoque['descricao'],
            id_conta_estoque
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Conta de estoque atualizada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar conta de estoque'}), 500

@conta_estoque_bp.route('/contas_estoque/<int:id_conta_estoque>', methods=['DELETE'])
@verifica_token
def deletar_conta_estoque(payload, id_conta_estoque):
    try:
        query = "DELETE FROM conta_estoque WHERE id_conta_estoque = %s"
        params = (id_conta_estoque,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Conta de estoque deletada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao deletar conta de estoque'}), 500
