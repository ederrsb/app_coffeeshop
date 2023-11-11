from flask import Blueprint, jsonify, request
from conexao_db import Conexao
import logging
from logger import logger

assinatura_bp = Blueprint('assinatura', __name__)

conexao = Conexao()

@assinatura_bp.route('/assinaturas', methods=['GET'])
def obter_assinaturas():
    try:
        query = 'SELECT * FROM assinatura'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            assinaturas = [dict(zip(colunas, assinatura)) for assinatura in resultado]
            return jsonify(assinaturas)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter assinaturas: {str(e)}")
        return jsonify({'message': 'Erro ao obter assinaturas'}), 500

@assinatura_bp.route('/assinaturas/<int:id_assinatura>', methods=['GET'])
def obter_assinatura(id_assinatura):
    try:
        query = 'SELECT * FROM assinatura WHERE id_assinatura = %s'
        resultado = conexao.execute_query(query, (id_assinatura,))

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            assinatura = dict(zip(colunas, resultado[0]))
            return jsonify(assinatura)
        else:
            return jsonify({'message': 'Assinatura não encontrada'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao obter assinatura'}), 500

@assinatura_bp.route('/assinaturas_item', methods=['GET'])
def obter_assinatura_item():
    try:
        id_cliente = request.args.get('id_cliente')
        id_assinatura = request.args.get('id_assinatura')
        periodicidade = request.args.get('periodicidade')
        id_item = request.args.get('id_item')
        status = request.args.get('status')

        # Inicializa uma lista de condições para a cláusula WHERE
        conditions = []

        if id_cliente:
            conditions.append("and a.id_cliente = %s")

        if id_assinatura:
            conditions.append("and a.id_assinatura = %s")

        if periodicidade:
            conditions.append("and a.periodicidade = %s")

        if id_item:
            conditions.append("and ai.id_item = %s")

        if status:
            conditions.append("and a.status = %s")

        # Constrói a cláusula WHERE combinando as condições com 'AND'
        where_clause = "".join(conditions) if conditions else ""

        # Constrói a consulta SQL com a cláusula WHERE
        query = f"""
                select a.id_cliente,
                       c.nome as nome_cliente,
                       a.id_assinatura,
                       a.descricao as desc_assinatura,
                       a.periodicidade,
                       ai.id_item,
                       i.descricao as desc_item,
                       ai.quantidade,
                       a.status
                  from assinatura a
                  join assinatura_item ai on a.id_assinatura = ai.id_assinatura
                  join item i on ai.id_item = i.id_item  
                  join cliente c on a.id_cliente = c.id_cliente 
                 where 1=1 {where_clause}
                 order by 1, 2, 3
                """

        # Parâmetros a serem passados na consulta
        params = [id_cliente, id_assinatura, periodicidade, id_item, status]

        # Remove None da lista de parâmetros para os que não foram fornecidos
        params = [param for param in params if param is not None]

        # Executa a consulta SQL
        resultado = conexao.execute_query(query, params)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            assinaturas_itens = [dict(zip(colunas, assinaturas_item)) for assinaturas_item in resultado]
            return jsonify(assinaturas_itens)
        else:
            return jsonify({'message': 'Item da Assinatura não encontrada'}), 404
    except Exception as e:
        logger.error(f"Erro ao obter itens das assinaturas: {str(e)}")
        return jsonify({'message': 'Erro ao obter item das assinaturas'}), 500
    
@assinatura_bp.route('/assinaturas', methods=['POST'])
def inserir_assinatura():
    try:
        dados_assinatura = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.assinatura (descricao, periodicidade, status, id_cliente) 
                VALUES (%s, %s, %s, %s)
                """

        params = (
            dados_assinatura['descricao'],
            dados_assinatura['periodicidade'],
            dados_assinatura['status'],
            dados_assinatura['id_cliente']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Assinatura inserida com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao inserir assinatura'}), 500

@assinatura_bp.route('/assinaturas/<int:id_assinatura>', methods=['PUT'])
def atualizar_assinatura(id_assinatura):
    try:
        dados_assinatura = request.get_json()

        query = """
                    UPDATE db_coffeeshop.assinatura
                    SET descricao = %s, periodicidade = %s, status = %s, id_cliente = %s
                    WHERE id_assinatura = %s
                """

        params = (
            dados_assinatura['descricao'],
            dados_assinatura['periodicidade'],
            dados_assinatura['status'],
            dados_assinatura['id_cliente'],
            id_assinatura
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Assinatura atualizada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar assinatura'}), 500

@assinatura_bp.route('/assinaturas/<int:id_assinatura>', methods=['DELETE'])
def deletar_assinatura(id_assinatura):
    try:
        query = "DELETE FROM db_coffeeshop.assinatura WHERE id_assinatura = %s"
        params = (id_assinatura,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Assinatura deletada com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao deletar assinatura'}), 500

@assinatura_bp.route('/assinatura_itens', methods=['POST'])
def inserir_assinatura_item():
    try:
        dados_assinatura_item = request.get_json()

        query = """
                    INSERT INTO db_coffeeshop.assinatura_item (id_assinatura, id_item, quantidade)
                    VALUES (%s, %s, %s)
                """

        params = (
            dados_assinatura_item['id_assinatura'],
            dados_assinatura_item['id_item'],
            dados_assinatura_item['quantidade']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de assinatura inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir item de assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao inserir item de assinatura'}), 500

@assinatura_bp.route('/assinatura_itens/<int:id_assinatura>/<int:id_item>', methods=['PUT'])
def atualizar_assinatura_item(id_assinatura, id_item):
    try:
        dados_assinatura_item = request.get_json()

        query = """
                    UPDATE db_coffeeshop.assinatura_item
                    SET quantidade = %s
                    WHERE id_assinatura = %s AND id_item = %s
                """

        params = (
            dados_assinatura_item['quantidade'],
            id_assinatura,
            id_item
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de assinatura atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar item de assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar item de assinatura'}), 500

@assinatura_bp.route('/assinatura_itens/<int:id_assinatura>/<int:id_item>', methods=['DELETE'])
def deletar_assinatura_item(id_assinatura, id_item):
    try:
        query = "DELETE FROM db_coffeeshop.assinatura_item WHERE id_assinatura = %s AND id_item = %s"
        params = (id_assinatura, id_item)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item de assinatura deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar item de assinatura: {str(e)}")
        return jsonify({'message': 'Erro ao deletar item de assinatura'}), 500