from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

# 对于 Vercel，我们使用内存数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义积分记录模型
class PointsRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False, default='辛巴')
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'points': self.points,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 初始化数据
with app.app_context():
    db.create_all()
    
    # 添加初始数据
    if PointsRecord.query.count() == 0:
        initial_records = [
            PointsRecord(user='辛巴', points=10, description='初始积分'),
            PointsRecord(user='泡芙', points=10, description='初始积分')
        ]
        db.session.add_all(initial_records)
        db.session.commit()

# API 路由
@app.route('/api/points', methods=['GET'])
def get_points():
    user = request.args.get('user', '辛巴')
    records = PointsRecord.query.filter_by(user=user).order_by(PointsRecord.created_at.desc()).all()
    total_points = sum(record.points for record in records)
    return jsonify({
        'total_points': total_points,
        'records': [record.to_dict() for record in records]
    })

@app.route('/api/points/add', methods=['POST'])
def add_points():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        points = data.get('points', 0)
        description = data.get('description', '增加积分')
        user = data.get('user', '辛巴')
        
        try:
            points = int(points)
        except (TypeError, ValueError):
            return jsonify({'error': '积分必须是整数'}), 400
        
        if points <= 0:
            return jsonify({'error': '积分必须为正数'}), 400
        
        record = PointsRecord(user=user, points=points, description=description)
        db.session.add(record)
        db.session.commit()
        
        return jsonify({'message': '积分添加成功', 'record': record.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/points/reduce', methods=['POST'])
def reduce_points():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        points = data.get('points', 0)
        description = data.get('description', '减少积分')
        user = data.get('user', '辛巴')
        
        try:
            points = int(points)
        except (TypeError, ValueError):
            return jsonify({'error': '积分必须是整数'}), 400
        
        if points <= 0:
            return jsonify({'error': '积分必须为正数'}), 400
        
        record = PointsRecord(user=user, points=-points, description=description)
        db.session.add(record)
        db.session.commit()
        
        return jsonify({'message': '积分减少成功', 'record': record.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/points/history', methods=['GET'])
def get_points_history():
    days = request.args.get('days', 7, type=int)
    user = request.args.get('user', '辛巴')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    daily_points = db.session.query(
        func.date(PointsRecord.created_at).label('date'),
        func.sum(PointsRecord.points).label('points')
    ).filter(
        PointsRecord.created_at.between(start_date, end_date),
        PointsRecord.user == user
    ).group_by(
        func.date(PointsRecord.created_at)
    ).all()
    
    result = [{'date': str(date), 'points': points} for date, points in daily_points]
    
    return jsonify(result)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.session.query(PointsRecord.user).distinct().all()
    return jsonify([user[0] for user in users])

# Vercel 处理函数
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('积分奖励系统 API 正在运行'.encode('utf-8'))
        return

# 如果直接运行此文件
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 