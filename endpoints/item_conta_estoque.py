from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger  # Certifique-se de importar o logger adequado

item_conta_estoque_bp = Blueprint('item_conta_estoque', __name__)
conexao = Conexao()

@item_conta_estoque_bp.route('/itens_conta_estoque', methods=['GET'])
def obter_itens_conta_estoque():
    try:
        query = 'SELECT * FROM item_conta_estoque'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            itens_conta_estoque = [dict(zip(colunas, item_conta_estoque)) for item_conta_estoque in resultado]
            return jsonify(itens_conta_estoque)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter itens de conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao obter itens de conta de estoque'}), 500

@item_conta_estoque_bp.route('/itens_conta_estoque', methods=['POST'])
def inserir_item_conta_estoque():
    try:
        dados_item_conta_estoque = request.get_json()

        query = """
                    INSERT INTO item_conta_estoque (id_item, id_conta_estoque, saldo, qtde_minima, qtde_maxima, data_atualizacao)
                    VALUES (%s, %s, %s, %s, %s, now())
                """

        params = (
            dados_item_conta_estoque['id_item'],
            dados_item_conta_estoque['id_conta_estoque'],
            dados_item_conta_estoque['saldo'],
            dados_item_conta_estoque['qtde_minima'],
            dados_item_conta_estoque['qtde_maxima']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de conta de estoque inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir item de conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao inserir item de conta de estoque'}), 500

@item_conta_estoque_bp.route('/itens_conta_estoque/<int:id_item>/<int:id_conta_estoque>', methods=['PUT'])
def atualizar_item_conta_estoque(id_item, id_conta_estoque):
    try:
        dados_item_conta_estoque = request.get_json()

        query = """
                    UPDATE item_conta_estoque
                    SET saldo = %s, qtde_minima = %s, qtde_maxima = %s, data_atualizacao = now()
                    WHERE id_item = %s AND id_conta_estoque = %s
                """

        params = (
            dados_item_conta_estoque['saldo'],
            dados_item_conta_estoque.get('qtde_minima', None),
            dados_item_conta_estoque.get('qtde_maxima', None),
            id_item,
            id_conta_estoque
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de conta de estoque atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar item de conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar item de conta de estoque'}), 500

@item_conta_estoque_bp.route('/itens_conta_estoque/<int:id_item>/<int:id_conta_estoque>', methods=['DELETE'])
def deletar_item_conta_estoque(id_item, id_conta_estoque):
    try:
        query = "DELETE FROM item_conta_estoque WHERE id_item = %s AND id_conta_estoque = %s"
        params = (id_item, id_conta_estoque)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de conta de estoque deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar item de conta de estoque: {str(e)}")
        return jsonify({'message': 'Erro ao deletar item de conta de estoque'}), 500
