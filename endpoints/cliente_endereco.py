from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

cliente_endereco_bp = Blueprint('cliente_endereco', __name__)

conexao = Conexao()

@cliente_endereco_bp.route('/clientes_endereco/<int:id_cliente>', methods=['GET'])
def obter_enderecos_cliente(id_cliente):
    try:
        query = 'SELECT * FROM cliente_endereco WHERE id_cliente = %s'
        resultado = conexao.execute_query(query, (id_cliente,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            enderecos = [dict(zip(colunas, endereco)) for endereco in resultado]
            return jsonify(enderecos)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter endereços do cliente: {str(e)}")
        return jsonify({'message': 'Erro ao obter endereços do cliente'}), 500

@cliente_endereco_bp.route('/clientes_endereco', methods=['POST'])
def inserir_endereco_cliente():
    try:
        dados_endereco = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.cliente_endereco (id_cliente, seq, rua, numero, bairro, cidade, cep, complemento, tipo_endereco)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_endereco['id_cliente'],
            dados_endereco['seq'],
            dados_endereco['rua'],
            dados_endereco['numero'],
            dados_endereco['bairro'],
            dados_endereco['cidade'],
            dados_endereco['cep'],
            dados_endereco['complemento'],
            dados_endereco['tipo_endereco']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Endereço do cliente inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir endereço do cliente: {str(e)}")
        return jsonify({'message': 'Erro ao inserir endereço do cliente'}), 500

@cliente_endereco_bp.route('/clientes_endereco/<int:id_cliente>/<int:seq>', methods=['PUT'])
def atualizar_endereco_cliente(id_cliente, seq):
    try:
        dados_endereco = request.get_json()

        query = """
                UPDATE db_coffeeshop.cliente_endereco
                SET rua = %s, numero = %s, bairro = %s, cidade = %s, cep = %s, complemento = %s, tipo_endereco = %s
                WHERE id_cliente = %s AND seq = %s
                """

        params = (
            dados_endereco['rua'],
            dados_endereco['numero'],
            dados_endereco['bairro'],
            dados_endereco['cidade'],
            dados_endereco['cep'],
            dados_endereco['complemento'],
            dados_endereco['tipo_endereco'],
            id_cliente,
            seq
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Endereço do cliente atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar endereço do cliente: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar endereço do cliente'}), 500

@cliente_endereco_bp.route('/clientes_endereco/<int:id_cliente>/<int:seq>', methods=['DELETE'])
def deletar_endereco_cliente(id_cliente, seq):
    try:
        query = "DELETE FROM db_coffeeshop.cliente_endereco WHERE id_cliente = %s AND seq = %s"
        params = (id_cliente, seq)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Endereço do cliente deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar endereço do cliente: {str(e)}")
        return jsonify({'message': 'Erro ao deletar endereço do cliente'}), 500
