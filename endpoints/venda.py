from flask import Blueprint, jsonify
from conexao_db import Conexao

venda_bp = Blueprint('venda', __name__)

conexao = Conexao()

@venda_bp.route('/vendas', methods=['GET'])
def obter_vendas():
    query = 'SELECT * FROM venda'
    resultado = conexao.execute_query(query)

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        vendas = [dict(zip(colunas, venda)) for venda in resultado]
        return jsonify(vendas)
    else:
        return jsonify([])  # Retorna uma lista vazia se não houver vendas

@venda_bp.route('/vendas/<int:id_venda>', methods=['GET'])
def obter_venda(id_venda):
    query = 'SELECT * FROM venda WHERE id_venda = %s'
    resultado = conexao.execute_query(query, (id_venda,))

    if resultado:
        colunas = [column[0] for column in conexao.cursor.description]
        venda = dict(zip(colunas, resultado[0]))
        return jsonify(venda)
    else:
        return jsonify({'message': 'Venda não encontrada'}), 404
