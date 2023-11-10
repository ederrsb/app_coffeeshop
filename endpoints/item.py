from flask import Blueprint, jsonify, request
from conexao_db import Conexao

item_bp = Blueprint('item', __name__)

conexao = Conexao()

@item_bp.route('/itens', methods=['GET'])
def obter_itens():
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
                                   where ice.id_item = i.id_item), 0) as saldo
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
        itens = [dict(zip(colunas, item)) for item in resultado]
        return jsonify(itens)
    else:
        return jsonify({'message': 'Item encontrada'}), 404