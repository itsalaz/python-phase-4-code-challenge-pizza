#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.get('/restaurants')
def restaurants():

    try:  
        restaurants = Restaurant.query.all()
        restaurant_list = [restaurant.to_dict() for restaurant in restaurants]

        return (restaurant_list), 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.get('/pizzas')
def pizzas():
    pizzas = Pizza.query.all()

    if pizzas:
        return [ pizza.to_dict() for pizza in pizzas ]
    else:
        return {'error': 'Pizza not found'}
    

@app.post('/restaurant_pizzas')
def make_restaurant_pizzas():
    data = request.json
    
    try:
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id = data['restaurant_id']
        
        if not all([price, pizza_id, restaurant_id]):
            return {'errors': ['validation errors']}, 400

        if not (1 <= price <= 30):
            return {'errors': ['validation errors']}, 400
        

        new_rp = RestaurantPizza(
            price= price, 
            pizza_id = pizza_id,
            restaurant_id = restaurant_id
        )

        db.session.add(new_rp)
        db.session.commit()

        
        return (new_rp.to_dict()), 201        
    
    
    except Exception as e:
        return {'errors': [str(e)]}, 400



@app.route('/pizzas/<int:id>', methods=['GET', 'POST', 'DELETE'])
def pizza_by_id(id):

    found_pizza = Pizza.query.filter_by(id = id).first()
    
    if request.method == 'GET':
        if found_pizza:
            return jsonify(found_pizza.to_dict()), 200
        else:
            return jsonify({'error': 'Pizza not found'})
    
    elif request.method == 'POST':
        data = request.json

        new_pizza = Pizza(
            name=data.get('name'), 
            ingredients=data.get('ingredients'),
        )

        db.session.add(new_pizza)
        db.session.commit()

        return jsonify(new_pizza.to_dict()), 201
    
    elif request.method == 'DELETE':

        if found_pizza:
            db.session.delete(found_pizza)
            db.session.commit()

        return {}, 204 
    else:
        return jsonify({'error': 'Pizza not found'}), 404
    
@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):

    found_restaurant = Restaurant.query.filter_by(id=id).first()


    if request.method == 'GET':
        if found_restaurant:
            return jsonify(found_restaurant.to_dict(include_pizzas=True)), 200
        else:
            return jsonify({'error': 'Restaurant not found'}), 404
    
    elif request.method == 'DELETE':
        if found_restaurant:
            db.session.delete(found_restaurant)
            db.session.commit()
            return {}, 204
        else:
            return jsonify({'error': 'Restaurant not found'}), 404




if __name__ == '__main__':
    app.run(port=5555, debug=True)
