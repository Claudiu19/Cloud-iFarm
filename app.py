import os
from os import path

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import api_calls
import db_controller
from db_controller import *
from Utils import *
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static\images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)  # create an app instance

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def hello():
    ads = db_controller.get_ads()
    for ad in ads:
        if ad['image_path']:
            if not path.exists(ad['image_path']):
                ad['image_path'] = None
    return render_template("ads.html", categories=read_categories(), title="Home", ads=ads)


@app.route("/categories")
def categories():
    cat_id = request.args['cat-id']
    if try_int(cat_id):
        cat_id = int(cat_id)
        category = get_category_by_id(cat_id)
        if len(category) == 0:
            title = "There is no such category"
            return render_template("ads.html", categories=read_categories(), title=title, ads=[])
        else:
            title = category[0]["en_cat_name"]
            return render_template("ads.html", categories=read_categories(), title=title, ads=db_controller.get_ads_by_category(cat_id))
    else:
        return render_template('404.html', title="Not Found")


@app.route("/confirm/<acc_key>")
def confirm_account(acc_key):
    if check_keys_format(acc_key):
        user_id = confirm_account(acc_key)
        if user_id != 0:
            return render_template('login.html', msg="Your account has been confirmed!")
        else:
            return render_template('login.html', msg="The link is not a correct one. Please try again more carefully.")
    else:
        return render_template('login.html', msg="The link is not a correct one. Please try again more carefully.")


@app.route("/translate/<target>", methods=["POST"])
def translate(target):
    if request.method == "POST" and "text" in request.get_json(force=True):
        if target == "ro":
            lang = "en-US"
        else:
            lang = "ro"
        resp = api_calls.translate_text(request.get_json(force=True)["text"], lang, target)
        return jsonify({"statusCode": "200", "translated_text": resp})
    else:
        return jsonify({"statusCode": "400", "message": "Bad Request"})


@app.route("/text_to_speech")
def text_to_speech():
    if request.method == "POST" and "text" in request.get_json(force=True):
        file_name = text_to_speech(request.get_json(force=True)["text"], "en-US")
        return jsonify({"statusCode": "200", "audio_src_file": file_name})
    else:
        return jsonify({"statusCode": "400", "message": "Bad Request"})


@app.route("/view_ad/<ID>")
def view_generic_ads(ID):
    ad = get_ad_by_id(ID)
    if ad['image_path']:
        if not path.exists(ad['image_path']):
            ad['image_path'] = None
        else:
            ad['image_path'] = '\\.\\' + ad['image_path']
    return render_template('add_details.html', ad=ad)


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
        account_phone = get_user_by_phone(phone)
        if account:
            msg = 'Email already registered!'
        elif check_email_format(email) is False:
            msg = 'Invalid email address!'
        elif check_phone_number_format(phone) is False:
            msg = 'Invalid phone number!'
        elif account_phone:
            msg = 'Phone already registered!'
        else:
            person_type = request.form['personType']
            cnp = request.form['CNP']
            cui = request.form['CUI']
            name = request.form['name']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            if person_type == 'pf':
                if check_cnp_format(cnp) is False:
                    msg = 'Invalid CNP!'
                elif not name:
                    msg = 'Invalid name!'
                else:
                    if 'trial' in request.form:
                        user_id = create_user(email, password, phone, name, latitude, longitude, True, None, None, cnp)
                        msg = 'You have successfully registered!'
                        key = create_account_key(user_id=user_id)
                        api_calls.gmail_api_send_email("emilb200@gmail.com", email, "noreply: iFarm confirmation email",
                                                       "Thank you for creating an account on our platform!\nOpen this link in your browser to generate your account:"
                                                       "https://ifarm-278213.ey.r.appspot.com/confirm/" + key)
                    else:
                        key = request.form['key']
                        if check_keys_format(key) is False:
                            msg = 'Invalid key!'
                        else:
                            user_id = create_user(email, password, phone, name, latitude, longitude, False, None, None, cnp)
                            msg = 'You have successfully registered!'
                            key = create_account_key(user_id=user_id)
                            api_calls.gmail_api_send_email("emilb200@gmail.com", email,
                                                           "noreply: iFarm confirmation email",
                                                           "Thank you for creating an account on our platform!\nOpen this link in your browser to generate your account:"
                                                           "https://ifarm-278213.ey.r.appspot.com/confirm/" + key)
            elif person_type == 'pj':
                if check_cui_format(cui) is False:
                    msg = 'Invalid CUI!'
                elif not name:
                    msg = 'Invalid name!'
                else:
                    if 'trial' in request.form:
                        user_id = create_user(email, password, phone, name, latitude, longitude, True, name, cui, None)
                        msg = 'You have successfully registered!'
                        key = create_account_key(user_id=user_id)
                        api_calls.gmail_api_send_email("emilb200@gmail.com", email, "noreply: iFarm confirmation email",
                                                       "Thank you for creating an account on our platform!\nOpen this link in your browser to generate your account:"
                                                       "https://ifarm-278213.ey.r.appspot.com/confirm/" + key)
                    else:
                        key = request.form['key']
                        if check_keys_format(key) is False:
                            msg = 'Invalid key!'
                        else:
                            user_id = create_user(email, password, phone, name, latitude, longitude, False, name, cui, None)
                            key = create_account_key(user_id=user_id)
                            api_calls.gmail_api_send_email("emilb200@gmail.com", email,
                                                           "noreply: iFarm confirmation email",
                                                           "Thank you for creating an account on our platform!\nOpen this link in your browser to generate your account:"
                                                           "https://ifarm-278213.ey.r.appspot.com/confirm/" + key)
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
    ads = get_ads_by_user(session['id'])
    for ad in ads:
        if ad['image_path']:
            if not path.exists(ad['image_path']):
                ad['image_path'] = None
    return render_template('my_account.html', account=account, ads=ads, categories=read_categories())


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    if 'loggedin' in session:
        ads = db_controller.get_ads()
        for ad in ads:
            if ad['image_path']:
                if not path.exists(ad['image_path']):
                    ad['image_path'] = None
        return render_template('home.html', name=session['name'], categories=read_categories(), title="Home", ads=ads)
    return redirect(url_for('login'))


@app.route("/search")
def search():
    tags = request.args.get("search").split(" ")
    ads = db_controller.search_by_tags(tags)
    for ad in ads:
        if ad['image_path']:
            if not path.exists(ad['image_path']):
                ad['image_path'] = None
    return render_template("home.html", categories=read_categories(), title="Home", ads=ads)


@app.route('/send_email_info_key', methods=['POST'])
def send_email_info_key():
    user_id = session["id"]
    if get_api_key(user_id) == "":
        key = add_api_key(user_id)
    else:
        key = get_api_key(user_id)
    api_calls.gmail_api_send_email("emilb200@gmail.com", session['email'], "noreply: iFarm upgrade account",
         "Hello! This is your iFarm API key: " + key)
    return jsonify("ok")


# API routes
@app.route("/api/ads/<ID>", methods=["GET"])
def generic_ads(ID):
    create_ads_table()
    data = get_ads_by_user(ID)
    return jsonify(data)


@app.route("/api/self_ads", methods=["GET"])
def specified_ads():
    key = request.args.get('api_key')
    user = get_user_of_key(key)
    data = get_ads_by_user(user)
    return jsonify(data)


@app.route("/api/post_ad", methods=["POST"])
def post_ad():
    key = request.args.get('api_key')
    description = request.args.get('description')
    name = request.args.get('title')
    category_id = request.args.get('category_id')
    tags_string_dict = request.args.get('tags_string_dict')
    status = 1
    user_id = get_user_of_key(key)
    image_path = request.args.get('image_path')
    insert_ad(user_id, name, description, category_id, tags_string_dict, image_path, status)
    redirect(url_for('my_account'))


@app.route("/api/disable_ad", methods=["PUT"])
def disable_ad():
    key = request.args.get('api_key')
    post_id = request.args.get('posting_id')
    status = request.args.get('status')
    user_id = get_user_of_key(key)
    update_ad_status(post_id, status, user_id)
    return jsonify({"Status": "200", "Message": "Status Updated!"})


# Error handlers
@app.errorhandler(500)
def server_error(e):
    log_string("iFarm_log", 'An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@app.errorhandler(404)
def server_error(e):
    log_string("iFarm_log", 'Accessed resource that doesnt exist!')
    return render_template("404.html")


@app.route("/create-ad", methods=["POST"])
def create_ad():
    user_id = session['id']
    name = request.form['name']
    description = request.form['description']
    category_id = request.form['category']
    tags_string_dict = request.form['tags']
    image_path = None
    status = 1

    if 'file' in request.files:
        file = request.files['file']
        if file.filename and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_path = file_path
            file.save(file_path)
            insert_ad(user_id, name, description, category_id, tags_string_dict, image_path, status)
    return redirect(url_for('my_account'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/ad/<ID>', methods=["GET"])
def ad_by_id(ID):
    account = get_user_by_id(session['id'])
    ad = get_ad_by_id(ID)
    if ad['image_path']:
        if not path.exists(ad['image_path']):
            ad['image_path'] = None
        else:
            ad['image_path'] = '\\.\\' + ad['image_path']
    return render_template('ad_details.html', account=account, ad=ad)


if __name__ == "__main__":  # on running python app.py
    app.secret_key = 'super secret key'
    app.run()
