from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:

	# remove/convert invalid chars
	recipeName = re.sub('-', ' ', recipeName)
	recipeName = re.sub('_', ' ', recipeName)
	recipeName = re.sub('[^a-zA-Z ]', '', recipeName)

	# handle string with no letters
	recipeName = recipeName.lower().strip()
	if not recipeName:
		return None
	
	# convert to list to individual words
	list = recipeName.split()

	# capitalise words
	list = [word.capitalize() for word in list]

	# return words with spaces between them
	return ' '.join(list)


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	entry = request.json

	# incorrect num of keys
	if len(entry) != 3:
		return 'invalid', 400

	if 'name' not in entry or 'type' not in entry:
		return 'no name or type', 400
	
	if entry['name'] in cookbook:
		return 'non unique entry name', 400

	if entry['type'] == 'recipe':
		if 'requiredItems' not in entry or len(entry['requiredItems']) == 0:
			return 'no requiredItems', 400
		
		for i in entry['requiredItems']:
			if len(i) != 2:
				return 'invalid requiredItem', 400

			if 'name' not in i or 'quantity' not in i:
				return 'invalid keys in requiredItems', 400
			
			if i['quantity'] < 0:
				return 'invalid quantity', 400
	
	elif entry['type'] == 'ingredient':
		if 'cookTime' not in entry:
			return 'no cookTime', 400
		
		if entry['cookTime'] < 0:
			return 'invalid cookTime', 400

	else:
		return 'invalid type', 400
	
	# delete name from entry and add entry to cookbook
	cookbook[entry.pop('name')] = entry
	
	return '', 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name = request.args['name']

	if name not in cookbook or cookbook[name]['type'] != 'recipe':
		return 'invalid name', 400

	ingredient_dict = {'cookTime': 0, 'ingredients': {}}
	if handle_recipe(name, ingredient_dict) == False:
		return 'couldnt handle recipe', 400

	result = {'name': name, 'cookTime': ingredient_dict['cookTime'], 'ingredients': []}
	for ingrName, quantity in ingredient_dict['ingredients'].items():
		result['ingredients'].append({'name': ingrName, 'quantity': quantity})

	return result, 200

def handle_recipe(name, ingredient_dict):
	for i in cookbook[name]['requiredItems']:
		item_name = i['name']

		if item_name not in cookbook:
			return False
		
		if cookbook[item_name] == 'recipe':
			return handle_recipe(item_name, ingredient_dict)
		
		else:
			ingredient_dict['ingredients'][item_name] = ingredient_dict['ingredients'].get(item_name, 0) + i['quantity']
			ingredient_dict['cookTime'] += cookbook[item_name]['cookTime'] * i['quantity']
			return True

# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
