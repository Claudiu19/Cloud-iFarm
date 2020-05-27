from app import db, error_client
from flask import Flask, render_template, request, Response
import sqlalchemy
import datetime
import Utils
from passlib.hash import pbkdf2_sha256
from decimal import *
import json


def drop_table(table):
    with db.connect() as conn:
        conn.execute(
            "DROP TABLE IF EXISTS " + table
        )


# Users
def create_users_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "  id INT NOT NULL AUTO_INCREMENT,"
            "  email varchar(255) UNIQUE NOT NULL,"
            "  password varchar(255) NOT NULL,"
            "  phone_number varchar(255) UNIQUE NOT NULL,"
            "  name varchar(255) NOT NULL,"
            "  latitude varchar(255),"
            "  longitude varchar(255),"
            "  date_joined DATETIME NOT NULL,"
            "  confirmed DATETIME NOT NULL,"
            "  trial BOOLEAN NOT NULL,"
            "  PRIMARY KEY(id)"
            ")"
        )


def create_person_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS persons ("
            " id INT NOT NULL AUTO_INCREMENT,"
            " cnp nvarchar(255) UNIQUE NOT NULL,"
            " user_id INT UNIQUE NOT NULL,"
            " PRIMARY KEY(id)"
            ")"
        )


def create_companies_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS companies ("
            " id INT NOT NULL AUTO_INCREMENT,"
            " cui nvarchar(255) UNIQUE NOT NULL,"
            " user_id INT UNIQUE NOT NULL,"
            " PRIMARY KEY(id)"
            ")"
        )


def create_confirmed_account():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS confirmed_account ("
            " id INT NOT NULL AUTO_INCREMENT,"
            " account_key nvarchar(255) UNIQUE NOT NULL,"
            " user_id INT UNIQUE NOT NULL,"
            " PRIMARY KEY(id)"
            ")"
        )


def create_session_token_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS session_tokens ("
            " token nvarchar(255) UNIQUE NOT NULL,"
            " user_id INT NOT NULL"
            ")"
        )


def create_user(email, password, phone_number, name, latitude, longitude, trial, company, cui=None, cnp=None):
    cmd_add_user = sqlalchemy.text("INSERT INTO users(email, password, phone_number, name, latitude, longitude, trial, confirmed) "
                                   "VALUES(:email, :password, :phone_number, :name, :latitude, :longitude, :trial, NULL)"
                                   )
    cmd_add_company = sqlalchemy.text("INSERT INTO company(cui, user_id) "
                                      "Values(:cui, :user_id)"
                                      )
    cmd_add_person = sqlalchemy.text("INSERT INTO persons(cnp, user_id) "
                                     "Values(:cnp, :user_id)"
                                     )
    with db.connect() as conn:
        conn.execute(cmd_add_user, email=email, password=pbkdf2_sha256.hash(password), phone_number=phone_number, name=name, latitude=latitude, longitude=longitude, trial=trial)
        user_id = conn.execute("LAST_INSERT_ID()").fetchone()[0]
        if company:
            conn.execute(cmd_add_company, cui=cui, user_id=user_id)
        else:
            conn.execute(cmd_add_person, cnp=cnp, user_id=user_id)
        return user_id


def create_account_key(user_id):
    cmd_add_account_key = sqlalchemy.text("INSERT INTO confirmed_account(user_id, account_key)"
                                          "VALUES(:user_id, :account_key)")
    key = Utils.generate_key()
    with db.connect() as conn:
        conn.execute(cmd_add_account_key, user_id=user_id, account_key=key)
        return key


def create_session_token(user_id):
    cmd_add_session_token = sqlalchemy.text("INSERT INTO session_tokens(token, user_id)"
                                            "VALUES(:token, :user_id)")
    key = Utils.generate_key()
    with db.connect() as conn:
        conn.execute(cmd_add_session_token, user_id=user_id, token=key)
        return key


def confirm_account(account_key):
    cmd_get_id = sqlalchemy.text("SELECT user_id FROM confirmed_account WHERE account_key = ':account_key'")
    if Utils.check_keys_format(account_key):
        with db.connect() as conn:
            rows = conn.execute(cmd_get_id, account_key=account_key)
            if rows.rowcount == 0:
                return 0
            else:
                row = rows.fetchone()
                user_id = row[0]
                conn.execute("UPDATE users SET confirmed='" + Utils.get_mysql_date(datetime.datetime.now()) + "' WHERE id=" + user_id)
                return user_id
    else:
        return 0


def check_session_token(session_token):
    cmd_get_id = sqlalchemy.text("SELECT user_id FROM session_tokens WHERE token = ':session_token'")
    if Utils.check_keys_format(session_token):
        with db.connect() as conn:
            rows = conn.execute(cmd_get_id, account_key=session_token)
            if rows.rowcount == 0:
                return 0
            else:
                row = rows.fetchone()
                user_id = row[0]
                return user_id
    else:
        return 0


def login_user(email):
    cmd_get_user = sqlalchemy.text("SELECT id, email, password FROM users WHERE email = :email")
    if Utils.check_email_format(email):
        with db.connect() as conn:
            rows = conn.execute(cmd_get_user, email=email)
            if rows.rowcount == 0:
                return {}
            else:
                row = rows.fetchone()
                return {"email": email, "hashed_pass": row[2], "user_id": row[0]} # pentru verificarea parolei: pbkdf2_sha256.verify(entered_password, hashed_password)
    else:
        return {}


# Categories
def create_categories_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS categories ("
            "  cat_id INT NOT NULL AUTO_INCREMENT,"
            "  ro_cat_name varchar(255) UNIQUE NOT NULL,"
            "  en_cat_name varchar(255) UNIQUE NOT NULL,"
            "  PRIMARY KEY(cat_id)"
            ")"
        )


def insert_categories(ro_cat_name, en_cat_name):
    command = sqlalchemy.text(
        "INSERT INTO categories(ro_cat_name, en_cat_name)"
        "VALUES(:ro_cat_name, :en_cat_name)"
    )
    with db.connect() as conn:
        conn.execute(command, ro_cat_name=ro_cat_name, en_cat_name=en_cat_name)


def read_categories():
    categories = []
    command = "SELECT cat_id, ro_cat_name, en_cat_name FROM categories"
    with db.connect() as conn:
        rows = conn.execute(command).fetchall()
        for row in rows:
            categories.append({"cat_id": row[0], "ro_cat_name": row[1], "en_cat_name": row[2]})

    return categories


def get_category_by_id(id):
    category = []
    command = "SELECT cat_id, ro_cat_name, en_cat_name FROM categories WHERE cat_id=" + str(id)
    with db.connect() as conn:
        rows = conn.execute(command).fetchall()
        for row in rows:
            category.append({"cat_id": row[0], "ro_cat_name": row[1], "en_cat_name": row[2]})
    return category


# Ads
def create_ads_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ads ("
            " id INT NOT NULL AUTO_INCREMENT,"
            " user_id INT NOT NULL,"
            " name nvarchar(255) NOT NULL,"
            " description TEXT NOT NULL,"
            " category_id INT NOT NULL,"
            " tags TEXT NOT NULL,"
            " date_created DATETIME NOT NULL,"
            " image_path nvarchar(100),"
            " status BOOLEAN NOT NULL,"
            " PRIMARY KEY(id)"
            ")"
        )


def get_ads():
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT A.id, A.name, A.description, A.category_id, A.tags, A.date_created"
            ", A.image_path, U.email, U.phone_number, U.name"
            " FROM ads A LEFT JOIN users U ON A.user_id = U.id WHERE A.status = 1"
        ).fetchall()
        ads = []
        for row in rows:
            ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3],
                        "tags": row[4], "date_created": row[5],
                        "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
            # ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3], "tags": json.loads(row[4])["tags"], "date_created": row[5],
            #             "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
        return ads


def get_ads_by_user(user_id):
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT A.id, A.name, A.description, A.category_id, A.tags, A.date_created"
            ", A.image_path, U.email, U.phone_number, U.name"
            " FROM ads A LEFT JOIN users U ON A.user_id = U.id WHERE A.status = 1 AND A.user_id = " + str(user_id)
        ).fetchall()
        ads = []
        for row in rows:
            ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3],
                        "tags": row[4], "date_created": row[5],
                        "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
            # ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3], "tags": json.loads(row[4])["tags"], "date_created": row[5],
            #             "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
        return ads


def get_ad_by_id(ad_id):
    with db.connect() as conn:
        # rows = conn.execute(
        #     "SELECT A.id, A.name, A.description, A.category_id, A.tags, A.date_created, A.image_path, U.email, U.phone_number, U.name"
        #     " FROM ads A LEFT JOIN users U ON A.user_id = U.id WHERE A.status = 1 AND A.id=" + str(ad_id)
        # ).fetchall()
        # ads = []
        # for row in rows:
        #     ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3],
        #                 "tags": row[4], "date_created": row[5],
        #                 "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
        #     # ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3], "tags": json.loads(row[4])["tags"], "date_created": row[5],
        #     #             "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
        # return ads

        rows = conn.execute(
            "SELECT A.id, A.name, A.description, A.category_id, A.tags, A.date_created, A.image_path, U.email, U.phone_number, U.name, U.latitude, U.longitude"
            " FROM ads A LEFT JOIN users U ON A.user_id = U.id WHERE A.status = 1 AND A.id=" + str(ad_id)
        )
        row = rows.fetchone()
        row_final = {"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3],
                     "tags": row[4], "date_created": row[5],
                     "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9], "latitude": row[10], "longitude": row[11]}
        if row_final["latitude"]:
            row_final["latitude"] = Decimal(row_final["latitude"])
        if row_final["longitude"]:
            row_final["longitude"] = Decimal(row_final["longitude"])
        return row_final


def get_ads_by_category(cat_id):
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT A.id, A.name, A.description, A.category_id, A.tags, A.date_created, A.image_path, U.email, U.phone_number, U.name"
            " FROM ads A LEFT JOIN users U ON A.user_id = U.id WHERE A.status = 1 AND A.category_id = " + str(cat_id)
        ).fetchall()
        ads = []
        for row in rows:
            ads.append({"id": row[0], "name": row[1], "description": row[2], "cat_id": row[3], "tags": json.loads(row[4])["tags"], "date_created": row[5],
                        "image_path": row[6], "contact_email": row[7], "contact_phone": row[8], "user_name": row[9]})
        return ads


def insert_ad(user_id, name, description, category_id, tags_string_dict, image_path, status): #tags_string_dict = json.dumps({"tags": [tag1, tag2...]})
    command = sqlalchemy.text(
        "INSERT INTO ads(user_id, name, description, category_id, tags, date_created, image_path, status)"
        " VALUES(:user_id, :name, :description, :category_id, :tags_string_dict, :date_created, :image_path, :status)"
    )
    with db.connect() as conn:
        conn.execute(command, user_id=user_id, name=name, description=description, category_id=category_id, tags_string_dict=tags_string_dict,
                     date_created=Utils.get_mysql_date(datetime.datetime.now()), image_path=image_path, status=status)


def update_ad_status(ad_id, status, user_id):
    try:
        if status:
            status = 1
        else:
            status = 0
        with db.connect() as conn:
            conn.execute("UPDATE ads SET status=" + str(status) + " Where id=" + str(ad_id) + " AND user_id=" + str(user_id))
            return True
    except:
        error_client.report_exception()
        return False


def delete_ad(ad_id, user_id):
    try:
        with db.connect() as conn:
            conn.execute("DELETE FROM ads WHERE id=" + str(ad_id) + " AND user_id=" + str(user_id))
            return True
    except:
        error_client.report_exception()
        return False


def search_by_tags(tags):
    ads = get_ads()

    relevant_ads = []
    for tag in tags:
        for ad in ads:
            ad_tags = ad["tags"].split(";")
            if tag in ad_tags and ad not in relevant_ads:
                relevant_ads.append(ad)
    return relevant_ads


# API keys
def create_api_keys_table():
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS api_keys("
            " user_id INT NOT NULL UNIQUE,"
            " api_key varchar(128) NOT NULL UNIQUE"
            ")"
        )


def add_api_key(user_id):
    try:
        key = Utils.generate_key()
        command = sqlalchemy.text("INSERT INTO api_keys(user_id, api_key) VALUES(:user_id, :api_key)")
        with db.connect() as conn:
            conn.execute(command, user_id=user_id, api_key=key)
            return key
    except:
        error_client.report_exception()
        return ""


def get_api_key(user_id):
    try:
        command = sqlalchemy.text("SELECT api_key from api_keys WHERE user_id=:user_id")
        with db.connect() as conn:
            rows = conn.execute(command, user_id=user_id)
            if rows.rowcount == 0:
                return ""
            else:
                row = rows.fetchone()
                return row[0]
    except:
        error_client.report_exception()
        return ""


def get_user_of_key(api_key):
    try:
        command = sqlalchemy.text("SELECT user_id from api_keys WHERE api_key=:api_key")
        with db.connect() as conn:
            rows = conn.execute(command, api_key=api_key)
            if rows.rowcount == 0:
                return 0
            else:
                row = rows.fetchone()
                return int(row[0])
    except:
        error_client.report_exception()
        return 0


def get_user_by_email_pass(email, password):
    try:
        command = sqlalchemy.text("SELECT id, email, password, phone_number, name, latitude, longitude"
                                  ", date_joined, confirmed, trial "
                                  " from users WHERE email=:email AND password=:password")
        with db.connect() as conn:
            rows = conn.execute(command, email=email, password=password)
            if rows.rowcount == 0:
                return None
            else:
                row = rows.fetchone()
                user = {'id': row[0], 'email': row[1], 'password': row[2], 'phone_number': row[3],
                        'name': row[4], 'latitude': row[5], 'longitude': row[6], 'date_joined': row[7],
                        'confirmed': row[8], 'trial': row[9]}
                return user
    except:
        error_client.report_exception()
        return None


def get_user_by_id(id_user):
    try:
        command = sqlalchemy.text("SELECT id, email, password, phone_number, name, latitude, longitude"
                                  ", date_joined, confirmed, trial "
                                  " from users WHERE id=:id")
        with db.connect() as conn:
            rows = conn.execute(command, id=id_user)
            if rows.rowcount == 0:
                return None
            else:
                row = rows.fetchone()
                user = {'id': row[0], 'email': row[1], 'password': row[2], 'phone_number': row[3],
                        'name': row[4], 'latitude': row[5], 'longitude': row[6], 'date_joined': row[7],
                        'confirmed': row[8], 'trial': row[9]}
                return user
    except:
        error_client.report_exception()
        return None
    
    
def get_user_by_phone(phone):
    try:
        command = sqlalchemy.text("SELECT id, email, password, phone_number, name, latitude, longitude"
                                  ", date_joined, confirmed, trial "
                                  " from users WHERE phone_number=:phone")
        with db.connect() as conn:
            rows = conn.execute(command, phone=phone)
            if rows.rowcount == 0:
                return None
            else:
                row = rows.fetchone()
                user = {'id': row[0], 'email': row[1], 'password': row[2], 'phone_number': row[3],
                        'name': row[4], 'latitude': row[5], 'longitude': row[6], 'date_joined': row[7],
                        'confirmed': row[8], 'trial': row[9]}
                return user
    except:
        error_client.report_exception()
        return None