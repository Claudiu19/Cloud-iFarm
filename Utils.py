import datetime
from app import s_acc, error_client
import re
from uuid import uuid4


def check_keys_format(key):
    if len(key) != 96:
        return False
    if re.match("^[a-z0-9]*$", key):
        return True
    else:
        return False


def check_email_format(email):
    if re.match('^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        return True
    else:
        return False


def check_cnp_format(cnp):
    if re.match('^[1-9]\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[1-4]\d|5[0-2]|99)(00[1-9]|0[1-9]\d|[1-9]\d\d)\d$', cnp):
        return True
    else:
        return False


def check_cui_format(cui):
    if re.match('^[1-9]*$', cui):
        return True
    else:
        return False


def check_phone_number_format(phone_number):
    if re.match('^(\+4|)?(07[0-8]{1}[0-9]{1}|02[0-9]{2}|03[0-9]{2}){1}?(\s|\.|\-)?([0-9]{3}(\s|\.|\-|)){2}$', phone_number):
        return True
    else:
        return False


def generate_key():
    key = uuid4().hex + uuid4().hex + uuid4().hex
    return key


def get_mysql_date(datetime_obj):
    date_format = '%Y-%m-%d %H:%M:%S'
    return datetime_obj.strftime(date_format)


def log_dict(log_name, log_data):
    try:
        from google.cloud import logging
        logging_client = logging.Client.from_service_account_json(s_acc)
        logger = logging_client.logger(log_name)
        logger.log_struct(log_data)
    except Exception:
        error_client.report_exception()


def log_string(log_name, log_data):
    try:
        from google.cloud import logging
        logging_client = logging.Client.from_service_account_json(s_acc)
        logger = logging_client.logger(log_name)
        logger.log_text(log_data)
    except Exception:
        error_client.report_exception()


def try_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



