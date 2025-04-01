from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///points_reward.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义积分记录模型
class PointsRecord(db.Model):
    """
    积分记录模型
    """
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False, default='辛巴')  # 用户名字段
    points = db.Column(db.Integer, nullable=False)  # 积分变动值
    description = db.Column(db.String(200))  # 描述
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    
    def to_dict(self):
        """
        将模型转换为字典
        """
        return {
            'id': self.id,
            'user': self.user,
            'points': self.points,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 检查是否需要添加初始用户数据
    if PointsRecord.query.count() == 0:
        # 为辛巴和泡芙添加初始积分记录
        initial_records = [
            PointsRecord(user='辛巴', points=10, description='初始积分'),
            PointsRecord(user='泡芙', points=10, description='初始积分')
        ]
        db.session.add_all(initial_records)
        db.session.commit()

# 模拟数据存储
points_data = {
    'points': 120,
    'history': [
        {
            'id': 1,
            'title': '完成数学作业',
            'time': '2024-01-20 15:30',
            'points': 10
        },
        {
            'id': 2,
            'title': '帮助同学',
            'time': '2024-01-20 14:20',
            'points': 5
        }
    ]
}

@app.route('/api/points', methods=['GET'])
def get_points():
    """
    获取总积分和积分记录
    """
    user = request.args.get('user', '辛巴')  # 默认为辛巴
    
    records = PointsRecord.query.filter_by(user=user).order_by(PointsRecord.created_at.desc()).all()
    total_points = sum(record.points for record in records)
    
    return jsonify({
        'total_points': total_points,
        'records': [record.to_dict() for record in records]
    })

@app.route('/api/points/add', methods=['POST'])
def add_points():
    """
    添加积分
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        points = data.get('points', 0)
        description = data.get('description', '增加积分')
        user = data.get('user', '辛巴')
        
        # 确保积分是整数
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
        print(f"添加积分时出错: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/points/reduce', methods=['POST'])
def reduce_points():
    """
    减少积分
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        points = data.get('points', 0)
        description = data.get('description', '减少积分')
        user = data.get('user', '辛巴')
        
        # 确保积分是整数
        try:
            points = int(points)
        except (TypeError, ValueError):
            return jsonify({'error': '积分必须是整数'}), 400
        
        if points <= 0:
            return jsonify({'error': '积分必须为正数'}), 400
        
        # 减少积分时，points 值为负数
        record = PointsRecord(user=user, points=-points, description=description)
        db.session.add(record)
        db.session.commit()
        
        return jsonify({'message': '积分减少成功', 'record': record.to_dict()})
    except Exception as e:
        db.session.rollback()
        print(f"减少积分时出错: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/points/history', methods=['GET'])
def get_points_history():
    """
    获取积分历史记录
    """
    days = request.args.get('days', 7, type=int)
    user = request.args.get('user', '辛巴')  # 默认为辛巴
    
    # 获取最近 days 天的积分记录
    from sqlalchemy import func
    from datetime import timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 按日期分组查询
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
    """
    获取所有用户
    """
    users = db.session.query(PointsRecord.user).distinct().all()
    return jsonify([user[0] for user in users])

if __name__ == '__main__':
    app.run(debug=True)