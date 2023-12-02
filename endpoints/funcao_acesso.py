from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

funcao_acesso_bp = Blueprint('funcao_acesso', __name__)

conexao = Conexao()

@funcao_acesso_bp.route('/funcoes-acesso', methods=['GET'])
@verifica_token
def obter_funcoes_acesso(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao_acesso'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Função Acesso'}), 403
    
    try:
        query = 'SELECT * FROM funcao_acesso'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            funcoes_acesso = [dict(zip(colunas, funcao_acesso)) for funcao_acesso in resultado]
            return jsonify(funcoes_acesso)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter funções de acesso: {str(e)}")
        return jsonify({'message': 'Erro ao obter funções de acesso'}), 500

@funcao_acesso_bp.route('/funcoes-acesso', methods=['POST'])
@verifica_token
def inserir_funcao_acesso(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao_acesso'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Função Acesso'}), 403
    
    try:
        dados_funcao_acesso = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.funcao_acesso (id_funcao, id_acesso, consultar, inserir, alterar, excluir)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_funcao_acesso['id_funcao'],
            dados_funcao_acesso['id_acesso'],
            dados_funcao_acesso['consultar'],
            dados_funcao_acesso['inserir'],
            dados_funcao_acesso['alterar'],
            dados_funcao_acesso['excluir'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função Acesso inserida com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir função de acesso: {str(e)}")
        return jsonify({'message': 'Erro ao inserir função de acesso'}), 500

@funcao_acesso_bp.route('/funcoes-acesso/<int:id_funcao>/<string:id_acesso>', methods=['PUT'])
@verifica_token
def atualizar_funcao_acesso(payload, id_funcao, id_acesso):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao_acesso'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Função Acesso'}), 403
    
    try:
        dados_funcao_acesso = request.get_json()

        query = """
                UPDATE db_coffeeshop.funcao_acesso
                SET consultar = %s, inserir = %s, alterar = %s, excluir = %s
                WHERE id_funcao = %s AND id_acesso = %s
                """

        params = (
            dados_funcao_acesso['consultar'],
            dados_funcao_acesso['inserir'],
            dados_funcao_acesso['alterar'],
            dados_funcao_acesso['excluir'],
            id_funcao,
            id_acesso,
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função Acesso atualizada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar função de acesso: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar função de acesso'}), 500

@funcao_acesso_bp.route('/funcoes-acesso/<int:id_funcao>/<string:id_acesso>', methods=['DELETE'])
@verifica_token
def deletar_funcao_acesso(payload, id_funcao, id_acesso):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'funcao_acesso'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Função Acesso'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.funcao_acesso WHERE id_funcao = %s AND id_acesso = %s"
        params = (id_funcao, id_acesso)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Função Acesso deletada com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao deletar função de acesso: {str(e)}")
        return jsonify({'message': 'Erro ao deletar função de acesso'}), 500
