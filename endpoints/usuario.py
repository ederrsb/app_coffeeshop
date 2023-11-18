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
    if not verifica_acesso(id_usuario, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Usuário'}), 403
    
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
def inserir_usuario(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Usuário'}), 403
    
    try:
        dados_usuario = request.get_json()

        # Adicione a criptografia para a senha
        senha_hashed = bcrypt.hashpw(dados_usuario['senha'].encode('utf-8'), bcrypt.gensalt())

        query = """
                INSERT INTO db_coffeeshop.usuario (id_cliente, id_funcionario, tipo_usuario, data_cadastro, email, senha, status)
                VALUES (%s, %s, %s, now(), %s, %s, %s)
                """

        params = (
            dados_usuario['id_cliente'],
            dados_usuario['id_funcionario'],
            dados_usuario['tipo_usuario'],
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
@verifica_token
def atualizar_usuario(payload, id_usuario):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Usuário'}), 403
    
    try:
        dados_usuario = request.get_json()

        # Adicione a criptografia para a senha, se fornecida
        senha_hashed = bcrypt.hashpw(dados_usuario.get('senha', '').encode('utf-8'), bcrypt.gensalt())

        query = """
                    UPDATE db_coffeeshop.usuario
                    SET id_cliente = %s, id_funcionario = %s, tipo_usuario = %s,
                        email = %s, senha = %s, status = %s
                    WHERE id_usuario = %s
                """

        params = (
            dados_usuario['id_cliente'],
            dados_usuario['id_funcionario'],
            dados_usuario['tipo_usuario'],
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
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'usuario'):
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
@verifica_token
def obter_usuarios2(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'usuario'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Usuário'}), 403
    
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
                    left join funcionario f on a.id_funcionario = f.id_funcionario
                    left join funcao f2 on f2.id_funcao = f.id_funcao
                    left join funcao_acesso fa on fa.id_funcao = coalesce(f2.id_funcao,
                                                                        (select f3.id_funcao  
                                                                            from funcao f3 
                                                                            where f3.descricao = 'Cliente'))
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
