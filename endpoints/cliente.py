from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

cliente_bp = Blueprint('cliente', __name__)

conexao = Conexao()

@cliente_bp.route('/clientes', methods=['GET'])
def obter_clientes():
    try:
        query = 'SELECT * FROM cliente'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            clientes = [dict(zip(colunas, cliente)) for cliente in resultado]
            return jsonify(clientes)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter clientes: {str(e)}")
        return jsonify({'message': 'Erro ao obter clientes'}), 500

@cliente_bp.route('/clientes', methods=['POST'])
def inserir_cliente():
    try:
        dados_cliente = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.cliente (nome, cpf, rg, nascimento, genero, celular)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_cliente['nome'],
            dados_cliente['cpf'],
            dados_cliente['rg'],
            dados_cliente['nascimento'],
            dados_cliente['genero'],
            dados_cliente.get('celular', None),
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Cliente inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir cliente: {str(e)}")
        return jsonify({'message': 'Erro ao inserir cliente'}), 500

@cliente_bp.route('/clientes/<int:id_cliente>', methods=['PUT'])
def atualizar_cliente(id_cliente):
    try:
        dados_cliente = request.get_json()

        query = """
                    UPDATE db_coffeeshop.cliente
                    SET nome = %s, cpf = %s, rg = %s, nascimento = %s, genero = %s, celular = %s
                    WHERE id_cliente = %s
                """

        params = (
            dados_cliente['nome'],
            dados_cliente['cpf'],
            dados_cliente['rg'],
            dados_cliente['nascimento'],
            dados_cliente['genero'],
            dados_cliente.get('celular', None),
            id_cliente
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Cliente atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar cliente'}), 500

@cliente_bp.route('/clientes/<int:id_cliente>', methods=['DELETE'])
def deletar_cliente(id_cliente):
    try:
        query = "DELETE FROM db_coffeeshop.cliente WHERE id_cliente = %s"
        params = (id_cliente,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {str(e)}")
        return jsonify({'message': 'Erro ao deletar cliente'}), 500
