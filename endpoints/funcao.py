from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

funcao_bp = Blueprint('funcao', __name__)

conexao = Conexao()

@funcao_bp.route('/funcoes', methods=['GET'])
@verifica_token
def obter_funcoes(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Função'}), 403
    
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
@verifica_token
def inserir_funcao(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Função'}), 403
    
    try:
        dados_funcao = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.funcao (nome, descricao)
                VALUES (%s, %s)
                """

        params = (
            dados_funcao['nome'],
            dados_funcao['descricao'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função inserida com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir função: {str(e)}")
        return jsonify({'message': 'Erro ao inserir função'}), 500

@funcao_bp.route('/funcoes/<int:id_funcao>', methods=['PUT'])
@verifica_token
def atualizar_funcao(payload, id_funcao):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Função'}), 403
    
    try:
        dados_funcao = request.get_json()

        query = """
                UPDATE db_coffeeshop.funcao
                SET nome = %s, descricao = %s
                WHERE id_funcao = %s
                """

        params = (
            dados_funcao['nome'],
            dados_funcao['descricao'],
            id_funcao
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função atualizada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar função: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar função'}), 500

@funcao_bp.route('/funcoes/<int:id_funcao>', methods=['DELETE'])
@verifica_token
def deletar_funcao(payload, id_funcao):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Função'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.funcao WHERE id_funcao = %s"
        params = (id_funcao,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função deletada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao deletar função: {str(e)}")
        return jsonify({'message': 'Erro ao deletar função'}), 500
