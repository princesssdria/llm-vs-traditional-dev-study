from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'

    #Create
    @app.route('/items', methods=['POST'])
    def add_item():
        data = request.get_json()
        new_item = Item(name=data['name'], price=data['price'])
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item created'}), 201
    #Read
    @app.route('/item/<int:item_id>',methods=['GET'])
    def get_item(item_id):
        item = Item.query.get_or_404(item_id)
        return jsonify({'name': item.name, 'price': item.price})
    #Update
    @app.route('/item/<int:item_id>', methods=['PUT'])
    def update_item(item_id):
        data = request.get_json()
        item = Item.query.get_or_404(item_id)
        item.name = data['name']
        item.price = data['price']
        db.session.commit()
        return jsonify({'message': 'Item updated'})
    #Delete
    @app.route('/item/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted'})

    if __name__ == '__main__':
        db.create_all() #Create database tables
        app.run(debug=True)