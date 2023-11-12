from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

funcao_bp = Blueprint('funcao', __name__)

conexao = Conexao()

@funcao_bp.route('/funcoes', methods=['GET'])
def obter_funcoes():
    try:
        query = 'SELECT * FROM funcao'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            funcoes = [dict(zip(colunas, funcao)) for funcao in resultado]
            return jsonify(funcoes)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter funções: {str(e)}")
        return jsonify({'message': 'Erro ao obter funções'}), 500

@funcao_bp.route('/funcoes', methods=['POST'])
def inserir_funcao():
    try:
        dados_funcao = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.funcao (descricao, prioridade)
                VALUES (%s, %s)
                """

        params = (
            dados_funcao['descricao'],
            dados_funcao['prioridade'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função inserida com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir função: {str(e)}")
        return jsonify({'message': 'Erro ao inserir função'}), 500

@funcao_bp.route('/funcoes/<int:id_funcao>', methods=['PUT'])
def atualizar_funcao(id_funcao):
    try:
        dados_funcao = request.get_json()

        query = """
                UPDATE db_coffeeshop.funcao
                SET descricao = %s, prioridade = %s
                WHERE id_funcao = %s
                """

        params = (
            dados_funcao['descricao'],
            dados_funcao['prioridade'],
            id_funcao
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função atualizada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar função: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar função'}), 500

@funcao_bp.route('/funcoes/<int:id_funcao>', methods=['DELETE'])
def deletar_funcao(id_funcao):
    try:
        query = "DELETE FROM db_coffeeshop.funcao WHERE id_funcao = %s"
        params = (id_funcao,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função deletada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar função: {str(e)}")
        return jsonify({'message': 'Erro ao deletar função'}), 500