# scrap.py

from flask import Blueprint, request, jsonify
from app import mysql

scrap_bp = Blueprint('scrap', __name__)

@scrap_bp.route('/delete_scrap/<int:scrap_id>', methods=['DELETE'])
def delete_scrap(scrap_id):
    try:
        # 데이터베이스에서 스크랩 삭제
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM scraps WHERE id = %s", (scrap_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)})
