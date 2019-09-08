"""Simple REST API.

There is a lot that can be done to improve the code here but I wanted to submit
a minimum viable product.
"""

from flask import Flask, request, make_response, jsonify
import sqlite3 as sql

app = Flask(__name__)
db_name = "q2.db"


def dict_factory(cursor, row):
    """Return sqlite information as dict, from:
    https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.errorhandler(404)
def page_not_found(error):
    """Page not found error."""
    return make_response(jsonify({"error": "Page not found"}), 404)


@app.route("/")
def index():
    return "Welcome to World Of Recipes!"


@app.route("/recipe/create", methods=["POST"])
def create_recipe():
    """Create recipe as POST request."""
    # Default response is server error
    result = make_response(jsonify({"success": "false"}), 500)

    if request.method == "POST":
        # Pull out data from request
        name = request.form["name"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]

        with sql.connect(db_name) as conn:
            conn.row_factory = dict_factory
            c = conn.cursor()

            c.execute(
                """
                INSERT OR REPLACE INTO recipes(name, description, ingredients)
                VALUES(?,?,?)
            """,
                (name, description, ingredients),
            )
            conn.commit()

            result = make_response(jsonify({"success": "true"}), 200)

    return result


@app.route("/recipe/edit", methods=["PATCH"])
def edit_recipe():
    """Update recipe in table."""
    # Default response is server error
    result = make_response(jsonify({"success": "false"}), 500)

    data = request.form

    # ID is compulsory
    if "recipe_id" not in data:
        return make_response(jsonify({"error": "ID must be defined"}), 400)

    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()

        # Check to see what to update
        if "name" in data:
            update = c.execute(
                """
                UPDATE recipes
                SET name = ?
                WHERE id = ?
            """,
                (data["name"], data["recipe_id"]),
            ).rowcount
        elif "description" in data:
            update = c.execute(
                """
                UPDATE recipes
                SET description = ?
                WHERE id = ?
            """,
                (data["description"], data["recipe_id"]),
            ).rowcount
        elif "ingredients" in data:
            update = c.execute(
                """
                UPDATE recipes
                SET ingredients = ?
                WHERE id = ?
            """,
                (data["ingredients"], data["recipe_id"]),
            ).rowcount

        conn.commit()

        if update == 1:
            result = make_response(jsonify({"success": "true"}), 200)
        elif update == 0:
            result = make_response(jsonify({"error": "ID not found"}), 404)

    return result


@app.route("/recipe", methods=["GET"])
def get_recipe():
    """Get recipe from table.

    If no `recipe_id` submitted, then all recipes are returned
    """
    # Default response is server error
    result = make_response(jsonify({"success": "false"}), 500)

    recipe_id = request.args.get("recipe_id", default=None)

    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()

        if recipe_id:
            # Selecting individual recipes
            result = c.execute(
                "SELECT * FROM recipes WHERE id=?", (int(recipe_id),)
            ).fetchone()
            conn.commit()
        else:
            # Selecting all recipes
            result = c.execute("SELECT * FROM recipes").fetchall()
            conn.commit()
            result = {"results": result}

        if result is None:
            # Return error if no recipe found for ids
            return make_response(jsonify({"error": "Recipe not found"}), 404)

    return result


@app.route("/recipe/delete", methods=["DELETE"])
def delete_recipe():
    """Delete recipe using `recipe_id`."""
    # Default response is server error
    result = make_response(jsonify({"success": "false"}), 500)

    recipe_id = request.args.get("recipe_id", default=None)

    if recipe_id is None:
        return {"error": "Must provide recipe_id"}

    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()

        delete = c.execute("DELETE FROM recipes WHERE id=?", (recipe_id,)).rowcount
        conn.commit()

        # Check if deletion was successful, rowcount = 1 for success
        if delete == 1:
            # Successful deletion
            result = make_response(jsonify({"success": "true"}), 200)
        elif delete == 0:
            # Unsuccessful deletion
            result = make_response(jsonify({"error": "ID not found"}), 404)

    return result


def create_db():
    """Create database when starting flask and add dummy data."""
    with sql.connect(db_name) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        # Kept ingredients as text for now
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes(
                id INTEGER PRIMARY KEY AUTOINCREMENT
                , name TEXT
                , description TEXT
                , ingredients TEXT
            )
        """
        )
        conn.commit()

        ### Uncomment to add simple dummy data ###
        # c.execute('''
        #     INSERT OR REPLACE INTO recipes(name, description, ingredients)
        #     VALUES(?,?,?)
        # ''', (
        #     'Club Sandwich',
        #     "Tesco's finest meal deal deli selection",
        #     '[chicken, bacon, horse meat probably, a ridiculous amount of mayonnaise]'
        # ))
        # conn.commit()


if __name__ == "__main__":
    create_db()

    app.run(debug=True)
