from flask import Blueprint, jsonify, request
from conexao_db import Conexao
from logger import logger
from login import verifica_token
from usuario import verifica_acesso
import base64

item_bp = Blueprint('item', __name__)
conexao = Conexao()

@item_bp.route('/itens', methods=['GET'])
@verifica_token
def obter_itens(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item'):
        return jsonify({'message': 'Usuário não possui acesso a consultar Item'}), 403
    
    try:
        query = 'SELECT * FROM Item'
        resultado = conexao.execute_query(query)

        if resultado:
            colunas = [column[0] for column in conexao.cursor.description]
            itens = [dict(zip(colunas, item)) for item in resultado]
            return jsonify(itens)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter itens: {str(e)}")
        return jsonify({'message': 'Erro ao obter itens'}), 500

@item_bp.route('/itens', methods=['POST'])
@verifica_token
def inserir_item(payload):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item'):
        return jsonify({'message': 'Usuário não possui acesso a inserir Item'}), 403
    
    try:
        dados_item = request.get_json()

        query = """
                INSERT INTO db_coffeeshop.Item (descricao, unid_medida, id_item_categoria, valor_unitario, data_atualizacao, status)
                VALUES (%s, %s, %s, %s, now(), 'A')
                """

        params = (
            dados_item['descricao'],
            dados_item['unid_medida'],
            dados_item['id_item_categoria'],
            dados_item['valor_unitario']
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item inserido com sucesso'}), 201
    except Exception as e:
        logger.error(f"Erro ao inserir item: {str(e)}")
        return jsonify({'message': 'Erro ao inserir item'}), 500

@item_bp.route('/itens/<int:id_item>', methods=['PUT'])
@verifica_token
def atualizar_item(payload, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item'):
        return jsonify({'message': 'Usuário não possui acesso a alterar Item'}), 403
    
    try:
        dados_item = request.get_json()

        query = """
                UPDATE db_coffeeshop.Item
                SET descricao = %s, unid_medida = %s, id_item_categoria = %s, valor_unitario = %s, data_atualizacao = now(), status = %s
                WHERE id_item = %s
                """

        params = (
            dados_item['descricao'],
            dados_item['unid_medida'],
            dados_item['id_item_categoria'],
            dados_item['valor_unitario'],
            dados_item['status'],
            id_item
        )

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item atualizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao atualizar item: {str(e)}")
        return jsonify({'message': 'Erro ao atualizar item'}), 500

@item_bp.route('/itens/<int:id_item>', methods=['DELETE'])
@verifica_token
def deletar_item(payload, id_item):
    id_usuario = payload['id_usuario']
    if not verifica_acesso(id_usuario, request.method, 'item'):
        return jsonify({'message': 'Usuário não possui acesso a excluir Item'}), 403
    
    try:
        query = "DELETE FROM db_coffeeshop.Item WHERE id_item = %s"
        params = (id_item,)

        conexao.execute_query(query, params)
        conexao.connection.commit()

        return jsonify({'message': 'Item deletado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar item: {str(e)}")
        return jsonify({'message': 'Erro ao deletar item'}), 500

@item_bp.route('/itens2', methods=['GET'])
def obter_itens2():
    
    id_item = request.args.get('id_item')
    desc_item = request.args.get('desc_item')
    id_item_categoria = request.args.get('id_item_categoria')
    desc_categoria = request.args.get('desc_categoria')
    status = request.args.get('status')
    sn_saldo = request.args.get('sn_saldo')

    # Inicializa uma lista de condições para a cláusula WHERE
    conditions = []

    # Adiciona a condição para o parâmetro 'tipo' se ele estiver presente
    if id_item:
        conditions.append("and a.id_item = %s")

    if desc_item:
        conditions.append("and a.desc_item like %s")

    if id_item_categoria:
        conditions.append("and a.id_item_categoria = %s")

    if desc_categoria:
        conditions.append("and a.desc_categoria like %s")

    if status:
        conditions.append("and a.status = %s")

    if sn_saldo:
        conditions.append("and %s = case when a.saldo = 0 then 'N' else 'S' end")

    # Constrói a cláusula WHERE combinando as condições com 'AND'
    where_clause = "".join(conditions) if conditions else ""

    # Constrói a consulta SQL com a cláusula WHERE
    query = f"""
        select *
          from (select i.id_item,
                       i.descricao as desc_item,
                       i.unid_medida,
                       i.id_item_categoria,
                       ic.descricao as desc_categoria,
                       i.valor_unitario,
                       i.data_atualizacao,
                       i.status,
                       coalesce((select sum(coalesce(ice.saldo, 0))
                                   from item_conta_estoque ice
                                   where ice.id_item = i.id_item), 0) as saldo,
                        i.imagem
                   from item i 
                   join item_categoria ic on i.id_item_categoria = ic.id_item_categoria) a  
         where 1=1 {where_clause}
         order by 1
    """

    # Parâmetros a serem passados na consulta
    params = [id_item, id_item_categoria, status, sn_saldo]

    if desc_item:
        params.append(f"%{desc_item}%")

    if desc_categoria:
        params.append(f"%{desc_categoria}%")

    # Remove None da lista de parâmetros para os que não foram fornecidos
    params = [param for param in params if param is not None]

    # Executa a consulta SQL
    resultado = conexao.execute_query(query, params)

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        # Converter bytes para base64 antes de criar o dicionário
        itens = []
        for item in resultado:
            item_dict = dict(zip(colunas, item))
            if 'imagem' in item_dict and item_dict['imagem'] is not None:
                item_dict['imagem'] = base64.b64encode(item_dict['imagem']).decode('utf-8')
            itens.append(item_dict)
        return jsonify(itens)
    else:
        return jsonify({'message': 'Item encontrada'}), 404