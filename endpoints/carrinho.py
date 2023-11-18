from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso

carrinho_bp = Blueprint('carrinho', __name__)

conexao = Conexao()

@carrinho_bp.route('/carrinhos/<int:id_cliente>', methods=['GET'])
@verifica_token
def obter_carrinhos_cliente(payload, id_cliente):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Carrinho'}), 403
    
    try:
        query = '''
                    select c.id_cliente,
                           c2.nome,
                           c.id_item,
                           i.descricao,
                           i.unid_medida,
                           c.quantidade,
                           c.data_atualizacao
                      from carrinho c 
                      join cliente c2 on c2.id_cliente  = c.id_cliente 
                      join Item i on i.id_item = c.id_item
                     where c.id_cliente = %s
                '''
        resultado = conexao.execute_query(query, (id_cliente,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            carrinhos = [dict(zip(colunas, carrinho)) for carrinho in resultado]
            return jsonify(carrinhos)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter carrinhos: {str(e)}")
        return jsonify({'message': 'Erro ao obter carrinhos'}), 500

@carrinho_bp.route('/carrinhos', methods=['POST'])
@verifica_token
def inserir_carrinho(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Carrinho'}), 403
    
    try:
        dados_carrinho = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.carrinho (id_cliente, id_item, quantidade, data_atualizacao)
                VALUES (%s, %s, %s, now())
                """

        params = (
            dados_carrinho['id_cliente'],
            dados_carrinho['id_item'],
            dados_carrinho['quantidade'],
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao inserir carrinho'}), 500

@carrinho_bp.route('/carrinhos/<int:id_cliente>/<int:id_item>', methods=['PUT'])
@verifica_token
def atualizar_carrinho(payload, id_cliente, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Carrinho'}), 403
    
    try:
        dados_carrinho = request.get_json()

        query = """
                UPDATE db_coffeeshop.carrinho
                SET quantidade = %s, data_atualizacao = now()
                WHERE id_cliente = %s AND id_item = %s
                """

        params = (
            dados_carrinho['quantidade'],
            id_cliente,
            id_item,
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar carrinho'}), 500

@carrinho_bp.route('/carrinhos/<int:id_cliente>/<int:id_item>', methods=['DELETE'])
@verifica_token
def deletar_carrinho(payload, id_cliente, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'carrinho'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Carrinho'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.carrinho WHERE id_cliente = %s AND id_item = %s"
        params = (id_cliente, id_item)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Carrinho deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar carrinho: {str(e)}")
        return jsonify({'message': 'Erro ao deletar carrinho'}), 500
