import datetime

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
project_id = "ifarm-278213"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

gmail_creds = "gmail_creds.json"
open_api_key = "qdJxqz27DQap3zxQSTpo_q75-qgrzHyiPCYrpj99yMEnxWUS_g"
