import sqlalchemy
import os
from google.cloud import error_reporting, logging

db_user = "root" #os.environ.get("DB_USER")
db_pass = "ryK25ywdbxD9qlkj" #os.environ.get("DB_PASS")
db_name = "iFarmDB" #os.environ.get("DB_NAME")
db_public_ip = "34.78.179.250" #os.environ.get("DB_PUBLIC_IP")
cloud_sql_connection_name = "ifarm-278213:europe-west1:ifarm" #os.environ.get("CLOUD_SQL_CONNECTION_NAME")
db = sqlalchemy.create_engine('mysql+pymysql://' + db_user + ':' + db_pass + '@' +
                              db_public_ip + '/' + db_name)

s_acc = "cloud_creds.json"
error_client = error_reporting.Client.from_service_account_json(s_acc)

gmail_api_key = "AIzaSyDFlXyb7YkMADs1KLJfB9TesmHiEUr0aPA"
gmail_api_client_id = "247564144410-vqh50fca77fgck0s35vpcpthj075j21c.apps.googleusercontent.com"
gmail_api_client_secret = "n8gkR0-QfrBOdI45k-HHBSLe"
open_api_key = "qdJxqz27DQap3zxQSTpo_q75-qgrzHyiPCYrpj99yMEnxWUS_g"
