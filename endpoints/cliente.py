from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

cliente_bp = Blueprint('cliente', __name__)

conexao = Conexao()

@cliente_bp.route('/clientes', methods=['GET'])
@verifica_token
def obter_clientes(payload):
    id_usuario = payload['id_usuario']
    # Se não tem acesso poderá consultar apenas o próprio
    if verifica_acesso(id_usuario, request.method, 'cliente'):
       id_usuario = '' 
    
    try:
        if id_usuario:
            query = f"SELECT * FROM cliente WHERE id_usuario = '{id_usuario}'"
        else:
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
                INSERT INTO db_coffeeshop.cliente (nome, cpf, rg, nascimento, genero, celular, id_usuario)
                VALUES (%s, %s, %s, str_to_date(%s, '%d/%m/%Y'), %s, %s, %s)
                """

        params = (
            dados_cliente['nome'],
            dados_cliente['cpf'],
            dados_cliente['rg'],
            dados_cliente['nascimento'],
            dados_cliente['genero'],
            dados_cliente.get('celular', None),
            dados_cliente.get('id_usuario', None),
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Cliente inserido com sucesso'}), 201
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao inserir cliente: {str(e)}")
        return jsonify({'message': 'Erro ao inserir cliente'}), 500

@cliente_bp.route('/clientes/<int:id_cliente>', methods=['PUT'])
@verifica_token
def atualizar_cliente(payload, id_cliente):
    id_usuario = payload['id_usuario']
    if verifica_acesso(id_usuario, request.method, 'cliente'):
       id_usuario = '' 
    
    try:
        dados_cliente = request.get_json()

        if id_usuario:
            query = f"""
                        UPDATE db_coffeeshop.cliente
                        SET nome = %s, cpf = %s, rg = %s, nascimento = %s, genero = %s, celular = %s
                        WHERE id_cliente = %s
                        and id_usuario = '{id_usuario}'
                    """
        else:
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
        conexao.connection.rollback()
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar cliente'}), 500

@cliente_bp.route('/clientes/<int:id_cliente>', methods=['DELETE'])
@verifica_token
def deletar_cliente(payload, id_cliente):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'cliente'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Cliente'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.cliente WHERE id_cliente = %s"
        params = (id_cliente,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
    except Exception as e:
        conexao.connection.rollback()
        logger.error(f"Erro ao deletar cliente: {str(e)}")
        return jsonify({'message': 'Erro ao deletar cliente'}), 500
