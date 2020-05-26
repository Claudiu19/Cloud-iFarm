from flask import Flask, render_template, request, redirect, url_for, session
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


#added
@app.route('/login', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # account = get_user_by_email_pass(email, password)
        account_logging = login_user(email)
        if account_logging:
            if pbkdf2_sha256.verify(password, account_logging['hashed_pass']):
                session['loggedin'] = True
                account = get_user_by_id(account_logging['user_id'])
                session['id'] = account['id']
                session['name'] = account['name']
                session['email'] = account['email']
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect password!'
        else:
            msg = 'Incorrect email!'
    return render_template('login.html', msg=msg)
    #return render_template("homePage.html", categories=read_categories(), title="Home", greeting="Hello World!")


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form \
            and 'phone' in request.form:
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        account = login_user(email)
        if account:
            msg = 'Account already exists!'
        elif check_email_format(email) is False:
            msg = 'Invalid email address!'
        elif check_phone_number_format(phone) is False:
            msg = 'Invalid phone number!'
        else:
            if 'trial' in request.form:
                create_user(email, password, phone, email, None, None, True, None, None, None)
                msg = 'You have successfully registered!'
            else:
                key = request.form['key']
                person_type = request.form['personType']
                cnp = request.form['CNP']
                cui = request.form['CUI']
                name = request.form['name']
                if check_keys_format(key) is False:
                    msg = 'Invalid key!'
                elif person_type == 'pf':
                    if check_cnp_format(cnp) is False:
                        msg = 'Invalid CNP!'
                    elif not name:
                        msg = 'Invalid name!'
                    else:
                        create_user(email, password, phone, name, None, None, False, None, None, cnp)
                        msg = 'You have successfully registered!'
                elif person_type == 'pj':
                    if check_cui_format(cui) is False:
                        msg = 'Invalid CUI!'
                    elif not name:
                        msg = 'Invalid name!'
                    else:
                        create_user(email, password, phone, name, None, None, False, name, cui, None)
                        msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['id'] = None
    session['name'] = None
    return redirect(url_for('login'))

@app.route('/my-account')
def my_account():
    account = get_user_by_id(session['id'])
    return render_template('my_account.html', account=account)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', name=session['name'])
    return redirect(url_for('login'))


if __name__ == "__main__":  # on running python app.py
    app.secret_key = 'super secret key'
    app.run()
