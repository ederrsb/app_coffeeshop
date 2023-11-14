from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
import bcrypt

usuario_bp = Blueprint('usuario', __name__)

conexao = Conexao()

@usuario_bp.route('/usuarios', methods=['GET'])
def obter_usuarios():
    try:
        query = 'SELECT * FROM usuario'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            usuarios = [dict(zip(colunas, usuario)) for usuario in resultado]
            return jsonify(usuarios)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter usuários: {str(e)}")
        return jsonify({'message': 'Erro ao obter usuários'}), 500
    
@usuario_bp.route('/usuarios', methods=['POST'])
def inserir_usuario():
    try:
        dados_usuario = request.get_json()

        # Adicione a criptografia para a senha
        senha_hashed = bcrypt.hashpw(dados_usuario['senha'].encode('utf-8'), bcrypt.gensalt())

        query = """
                INSERT INTO db_coffeeshop.usuario (id_cliente, id_funcionario, tipo_usuario, data_cadastro, email, senha, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

        params = (
            dados_usuario['id_cliente'],
            dados_usuario['id_funcionario'],
            dados_usuario['tipo_usuario'],
            dados_usuario['data_cadastro'],
            dados_usuario['email'],
            senha_hashed,
            dados_usuario['status']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Usuário inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir usuário: {str(e)}")
        return jsonify({'message': 'Erro ao inserir usuário'}), 500

@usuario_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def atualizar_usuario(id_usuario):
    try:
        dados_usuario = request.get_json()

        # Adicione a criptografia para a senha, se fornecida
        senha_hashed = bcrypt.hashpw(dados_usuario.get('senha', '').encode('utf-8'), bcrypt.gensalt())

        query = """
                    UPDATE db_coffeeshop.usuario
                    SET id_cliente = %s, id_funcionario = %s, tipo_usuario = %s,
                        data_cadastro = %s, email = %s, senha = %s, status = %s
                    WHERE id_usuario = %s
                """

        params = (
            dados_usuario['id_cliente'],
            dados_usuario['id_funcionario'],
            dados_usuario['tipo_usuario'],
            dados_usuario['data_cadastro'],
            dados_usuario['email'],
            senha_hashed,
            dados_usuario['status'],
            id_usuario
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Usuário atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar usuário'}), 500

@usuario_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):
    try:
        query = "DELETE FROM db_coffeeshop.usuario WHERE id_usuario = %s"
        params = (id_usuario,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {str(e)}")
        return jsonify({'message': 'Erro ao deletar usuário'}), 500

from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

usuario_bp = Blueprint('usuario', __name__)
conexao = Conexao()

@usuario_bp.route('/usuarios2', methods=['GET'])
def obter_usuarios2():
    try:
        tipo_usuario = request.args.get('tipo_usuario', default=None, type=str)
        id_usuario = request.args.get('id_usuario', default=None, type=int)
        id = request.args.get('id', default=None, type=int)
        status = request.args.get('status', default=None, type=str)

        # Inicializa uma lista de condições para a cláusula WHERE
        conditions = []

        # Adiciona a condição para o parâmetro 'tipo_usuario' se ele estiver presente
        if tipo_usuario:
            conditions.append("AND CASE WHEN u.tipo_usuario = 'C' THEN 'Cliente' ELSE 'Funcionário' END = %s")

        # Adiciona a condição para o parâmetro 'id_usuario' se ele estiver presente
        if id_usuario:
            conditions.append("AND u.id_usuario = %s")

        # Adiciona a condição para o parâmetro 'id' se ele estiver presente
        if id:
            conditions.append("AND COALESCE(u.id_cliente, u.id_funcionario) = %s")

        # Adiciona a condição para o parâmetro 'status' se ele estiver presente
        if status:
            conditions.append("AND u.status = %s")

        # Constrói a cláusula WHERE combinando as condições com 'AND'
        where_clause = " ".join(conditions)

        # Constrói a consulta SQL com a cláusula WHERE
        query = f"""
                    SELECT
                        CASE WHEN u.tipo_usuario = 'C' THEN 'Cliente' ELSE 'Funcionário' END AS tipo_usuario,
                        COALESCE(u.id_cliente, u.id_funcionario) AS id,
                        COALESCE(c.nome, f.nome) AS nome,
                        u.id_usuario,
                        u.data_cadastro,
                        u.email,
                        u.status
                    FROM usuario u
                    LEFT JOIN cliente c ON c.id_cliente = u.id_cliente
                    LEFT JOIN funcionario f ON f.id_funcionario = u.id_funcionario
                    WHERE 1=1 {where_clause}
                """

        # Parâmetros a serem passados na consulta
        params = [tipo_usuario, id_usuario, id, status]

        # Remove None da lista de parâmetros para os que não foram fornecidos
        params = [param for param in params if param is not None]

        # Executa a consulta SQL
        resultado = conexao.execute_query(query, params)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            usuarios = [dict(zip(colunas, usuario)) for usuario in resultado]
            return jsonify(usuarios)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter usuários: {str(e)}")
        return jsonify({'message': 'Erro ao obter usuários'}), 500