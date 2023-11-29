from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

item_categoria_bp = Blueprint('item_categoria', __name__)

conexao = Conexao()

@item_categoria_bp.route('/itens_categoria', methods=['GET'])
@verifica_token
def obter_itens_categoria(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item_categoria'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Categoria de Item'}), 403
    
    try:
        query = 'SELECT * FROM item_categoria'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            itens_categoria = [dict(zip(colunas, item_categoria)) for item_categoria in resultado]
            return jsonify(itens_categoria)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter categorias de itens: {str(e)}")
        return jsonify({'message': 'Erro ao obter categorias de itens'}), 500

@item_categoria_bp.route('/itens_categoria', methods=['POST'])
@verifica_token
def inserir_item_categoria(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item_categoria'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Categoria de Item'}), 403
    
    try:
        dados_item_categoria = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.item_categoria (descricao)
                VALUES (%s)
                """

        params = (
            dados_item_categoria['descricao'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Categoria de item inserida com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir categoria de item: {str(e)}")
        return jsonify({'message': 'Erro ao inserir categoria de item'}), 500

@item_categoria_bp.route('/itens_categoria/<int:id_item_categoria>', methods=['PUT'])
@verifica_token
def atualizar_item_categoria(payload, id_item_categoria):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item_categoria'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Categoria de Item'}), 403
    
    try:
        dados_item_categoria = request.get_json()

        query = """
                UPDATE db_coffeeshop.item_categoria
                SET descricao = %s
                WHERE id_item_categoria = %s
                """

        params = (
            dados_item_categoria['descricao'],
            id_item_categoria
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Categoria de item atualizada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar categoria de item: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar categoria de item'}), 500

@item_categoria_bp.route('/itens_categoria/<int:id_item_categoria>', methods=['DELETE'])
@verifica_token
def deletar_item_categoria(payload, id_item_categoria):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item_categoria'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Categoria de Item'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.item_categoria WHERE id_item_categoria = %s"
        params = (id_item_categoria,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Categoria de item deletada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar categoria de item: {str(e)}")
        return jsonify({'message': 'Erro ao deletar categoria de item'}), 500
