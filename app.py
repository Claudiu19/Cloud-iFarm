from flask import Flask, render_template, request
from db_controller import *
from Utils import *

app = Flask(__name__)  # create an app instance


@app.route("/")
def hello():
    return render_template("homePage.html", categories=read_categories(), title="Home", greeting="Hello World!")


@app.route("/categories")
def categories():
    title = ""
    greeting = ""
    cat_id = request.args['cat-id']
    if try_int(cat_id):
        cat_id = int(cat_id)
        category = get_category_by_id(cat_id)
        if len(category) == 0:
            title = "No such category"
            greeting = "No such category"
        else:
            title = category[0]["ro_cat_name"]
            greeting = category[0]["ro_cat_name"]
    all_categories = read_categories()
    return render_template("homePage.html", categories=all_categories, title=title, greeting=greeting)



@app.route("/<name>")
def hello_name(name):
    return "Hello " + name


if __name__ == "__main__":  # on running python app.py
    app.run()
