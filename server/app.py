from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = []
        for message in Message.query.order_by(Message.created_at.asc()).all():
            message_dict = {
                "id": message.id,
                "body": message.body,
                "username": message.username,
                "created_at": message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            messages.append(message_dict)
        return jsonify(messages), 200

    elif request.method == "POST":
        data = request.get_json()
        new_message = Message(
            body=data['body'],
            username=data['username'],
            created_at=datetime.utcnow(),
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = db.session.query(Message).get(id)  # Use db.session.query
    if not message:
        return jsonify({"error": "Message not found"}), 404

    if request.method == "PATCH":
        data = request.get_json()
        message.body = data['body']
        db.session.commit()
        return jsonify(message.to_dict()), 200

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(port=5555)