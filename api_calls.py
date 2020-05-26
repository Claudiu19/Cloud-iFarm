import uuid
from email.mime.text import MIMEText

import requests
import json

import Utils
from app import *
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def validate_company_cui(cui):
    url = "https://api.openapi.ro/api/companies/" + cui
    headers = {"content-type": "application/json", "x-api-key": open_api_key}
    if requests.get(url, headers=headers).status_code == 200:
        return True
    else:
        return False


def validate_person_cnp(cnp):
    url = "https://api.openapi.ro/api/validate/cnp/" + cnp
    headers = {"content-type": "application/json", "x-api-key": open_api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if response.json()["valid"]:
            return True
        else:
            return False
    else:
        return False


def create_gmail_api_object():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                gmail_creds, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    import base64
    res = base64.urlsafe_b64encode(message.as_bytes())
    res = res.decode()
    return {'raw': res}


def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return True
    except:
        error_client.report_exception()
        return False


def gmail_api_send_email(sender, to, subject, message_text):
    service = create_gmail_api_object()
    message = create_message(sender, to, subject, message_text)
    return send_message(service, 'me', message)


def text_to_speech(text, target):
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient.from_service_account_json(s_acc)
    synthesis_input = texttospeech.types.cloud_tts_pb2.SynthesisInput(text=text)
    voice = texttospeech.types.cloud_tts_pb2.VoiceSelectionParams(
        language_code=target,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.cloud_tts_pb2.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    file_name = 'Audio/' + str(uuid.uuid4()) + ".mp3"
    with open(file_name, 'wb') as out:
        out.write(response.audio_content)
    Utils.log_string("text_to_speech_log", "Generated file " + file_name + " for the text \"" + text + "\".")
    return file_name


def translate_text(text: str = "", lang: str = "en-US", target: str = "ro"):
    try:
        from google.cloud import translate
        if text != "":
            # storage_client = storage.Client()
            client = translate.TranslationServiceClient.from_service_account_json(s_acc)
            parent = client.location_path(project_id, "global")
            response = client.translate_text(
                parent=parent,
                contents=[text],
                mime_type="text/plain",  # mime types: text/plain, text/html
                source_language_code=lang,
                target_language_code=target,
            )
            resp = []
            Utils.log_string("translation_log", "Translated text \"" + text + "\" from \"" + lang + "\" to \"" + target + "\".")
            for translation in response.translations:
                resp.append({"translation": translation.translated_text})
            return resp
    except Exception:
        error_client.report_exception()

