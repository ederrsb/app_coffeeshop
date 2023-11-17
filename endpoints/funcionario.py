from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token

funcionario_bp = Blueprint('funcionario', __name__)

conexao = Conexao()

@funcionario_bp.route('/funcionarios', methods=['GET'])
@verifica_token
def obter_funcionarios(payload):
    try:
        query = 'SELECT * FROM funcionario'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            funcionarios = [dict(zip(colunas, funcionario)) for funcionario in resultado]
            return jsonify(funcionarios)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter funcionários: {str(e)}")
        return jsonify({'message': 'Erro ao obter funcionários'}), 500
    
@funcionario_bp.route('/funcionarios', methods=['POST'])
@verifica_token
def inserir_funcionario(payload):
    try:
        dados_funcionario = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.funcionario (nome, id_funcao, data_admissao, data_rescisao) 
                VALUES (%s, %s, %s, %s)
                """

        params = (
            dados_funcionario['nome'],
            dados_funcionario['id_funcao'],
            dados_funcionario['data_admissao'],
            dados_funcionario.get('data_rescisao', None)  # Campo opcional
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Funcionário inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir funcionário: {str(e)}")
        return jsonify({'message': 'Erro ao inserir funcionário'}), 500

@funcionario_bp.route('/funcionarios/<int:id_funcionario>', methods=['PUT'])
@verifica_token
def atualizar_funcionario(payload, id_funcionario):
    try:
        dados_funcionario = request.get_json()

        query = """
                UPDATE db_coffeeshop.funcionario
                SET nome = %s, id_funcao = %s, data_admissao = %s, data_rescisao = %s
                WHERE id_funcionario = %s
                """

        params = (
            dados_funcionario['nome'],
            dados_funcionario['id_funcao'],
            dados_funcionario['data_admissao'],
            dados_funcionario.get('data_rescisao', None),  # Campo opcional
            id_funcionario
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Funcionário atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar funcionário: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar funcionário'}), 500

@funcionario_bp.route('/funcionarios/<int:id_funcionario>', methods=['DELETE'])
@verifica_token
def deletar_funcionario(payload, id_funcionario):
    try:
        query = "DELETE FROM db_coffeeshop.funcionario WHERE id_funcionario = %s"
        params = (id_funcionario,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Funcionário deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar funcionário: {str(e)}")
        return jsonify({'message': 'Erro ao deletar funcionário'}), 500
