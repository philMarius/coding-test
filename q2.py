'''Simple REST API.'''

from flask import Flask, request, make_response, jsonify
from os import path
import sqlite3 as sql

app = Flask(__name__)
db_name = 'q2.db'

def dict_factory(cursor, row):
    '''Return sqlite information as dict, from:
    https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    '''
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.errorhandler(404)
def page_not_found(error):
    '''Page not found error.'''
    return make_response(jsonify({'error': 'Page not found'}), 404)

@app.route('/')
def index():
    return "Welcome to World Of Recipes!"

def create_recipe():
    pass

def edit_recipe():
    pass

@app.route('/recipe')
def get_recipe(methods=['GET',]):
    '''Get recipe from table.'''
    result = {'hello': 'there'}

    recipe_id = request.args.get('recipe_id', default=None)

    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()

        if recipe_id:
            # Selecting individual recipes
            result = c.execute(
                "SELECT * FROM recipes WHERE id=?",
                (int(recipe_id),)
            ).fetchone()
            conn.commit()
        else:
            # Selecting all recipes
            result = c.execute(
                "SELECT * FROM recipes"
            ).fetchone()
            conn.commit()

        if result is None:
            # Return error if no recipe found for ids
            return {'error': 'Recipe not found'}

    return result

def delete_recipe():
    pass

def create_db():
    '''Create database when starting flask.'''
    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        # Kept ingredients as text for now
        c.execute('''
            CREATE TABLE IF NOT EXISTS recipes(
                id INTEGER PRIMARY KEY AUTOINCREMENT
                , name TEXT
                , description TEXT
                , ingredients TEXT
            )
        ''')
        conn.commit()

        c.execute('''
            INSERT OR REPLACE INTO recipes(name, description, ingredients)
            VALUES(?,?,?)
        ''', (
            # 0,
            'Club Sandwich',
            "Tesco's finest meal deal deli selection",
            '[chicken, bacon, horse meat probably, a ridiculous amount of mayonnaise]'
        ))
        conn.commit()

if __name__ == '__main__':
    create_db()

    app.run(debug=True)
