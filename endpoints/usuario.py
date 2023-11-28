from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
import bcrypt

usuario_bp = Blueprint('usuario', __name__)
conexao = Conexao()

@usuario_bp.route('/usuarios', methods=['GET'])
@verifica_token
def obter_usuarios(payload):
    id_usuario = payload['id_usuario']
    # Se não tem acesso poderá consultar apenas o próprio
    if verifica_acesso(id_usuario, request.method, 'cliente'):
       id_usuario = '' 
    
    try:
        if id_usuario:
            query = f"SELECT * FROM usuario WHERE id_usuario = '{id_usuario}'"
        else:
            query = "SELECT * FROM usuario"

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
                INSERT INTO db_coffeeshop.usuario (data_cadastro, email, senha, status)
                VALUES (now(), %s, %s, 'A')
                """

        params = (
            dados_usuario['email'],
            senha_hashed
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Usuário inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir usuário: {str(e)}")
        return jsonify({'message': 'Erro ao inserir usuário'}), 500

@usuario_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@verifica_token
def atualizar_usuario(payload, id_usuario):
    id_usuario_logado = payload['id_usuario']
    if not verifica_acesso(id_usuario_logado, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Usuário'}), 403
    
    try:
        dados_usuario = request.get_json()

        # Adicione a criptografia para a senha, se fornecida
        senha_hashed = bcrypt.hashpw(dados_usuario.get('senha', '').encode('utf-8'), bcrypt.gensalt())

        query = """
                    UPDATE db_coffeeshop.usuario
                    SET email = %s, senha = %s, status = %s
                    WHERE id_usuario = %s
                """

        params = (
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
@verifica_token
def deletar_usuario(payload, id_usuario):
    id_usuario_logado = payload['id_usuario']
    if not verifica_acesso(id_usuario_logado, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Usuário'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.usuario WHERE id_usuario = %s"
        params = (id_usuario,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {str(e)}")
        return jsonify({'message': 'Erro ao deletar usuário'}), 500
    
@usuario_bp.route('/usuarios2', methods=['GET'])
def verifica_acesso(id_usuario, tipo, acesso):
    try:
        if tipo == 'GET':
            tipo = 'consultar'
        elif tipo == 'POST':
            tipo = 'inserir'
        elif tipo == 'PUT':
            tipo = 'alterar'
        elif tipo == 'DELETE':
            tipo = 'excluir'
        query = """
                  select case when count(1) = 0 then 'N' else 'S' end as possui_acesso
                    from usuario a
                    left join funcionario f on f.id_usuario = a.id_usuario
                    left join funcao f2 on f2.id_funcao = f.id_funcao
                    left join funcao_acesso fa on fa.id_funcao = coalesce(f2.id_funcao,
                                                                        (select f3.id_funcao  
                                                                            from funcao f3 
                                                                           where f3.nome = 'Cliente'))
                  where a.status = 'A'
                    and fa.id_acesso = %s
                    and a.id_usuario = %s
                    and case when %s = 'consultar' and fa.consultar = 'S' then 'S'
                             when %s = 'inserir'   and fa.inserir   = 'S' then 'S'
                             when %s = 'alterar'   and fa.alterar   = 'S' then 'S'
                             when %s = 'excluir'   and fa.excluir   = 'S' then 'S'
                        end = 'S';
                """
        params = (acesso, id_usuario, tipo, tipo, tipo, tipo)
        logger.info(acesso)
        logger.info(id_usuario)
        logger.info(tipo)
        resultado = conexao.execute_query(query, params)
        logger.info(resultado[0][0])
        return resultado[0][0] == 'S'
    except Exception as e:
        logger.error(f"Erro ao verificar acesso: {str(e)}")
        return False
        return jsonify({'message': 'Erro ao deletar usuário'}), 500