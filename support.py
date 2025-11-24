from io import BytesIO
import json
import os
import pycurl
import streamlit as st
from io import StringIO

#@st.cache_data
def download_get_url(url, headers):
    client = pycurl.Curl()
    #client.setopt(client.URL, url)
    client.setopt(pycurl.URL, url.encode("utf-8"))
    buffer = BytesIO()
    client.setopt(client.WRITEDATA, buffer)
    client.setopt(pycurl.USERAGENT, "BeruskaApp/1.2 (+tomas.vlasaty8@gmail.cz; https://jomipon-beruska-prototyp.streamlit.app/)")
    if headers is not None and len(headers) > 0:
        client.setopt(pycurl.HTTPHEADER, headers)
    # Volitelně debug:
    # client.setopt(pycurl.VERBOSE, True)
    client.perform()
    status = client.getinfo(pycurl.RESPONSE_CODE)
    #print(status)
    client.close()
    body = buffer.getvalue()
    return body

#@st.cache_data
def download_post_url(url, post_data, headers):
    if post_data.strip().startswith("{") or post_data.strip().startswith("["):
        post_data = (
            post_data
            .replace(": True", ": true")
            .replace(": False", ": false")
            .replace(": None", ": null")
        )
    client = pycurl.Curl()
    client.setopt(client.URL, url)
    client.setopt(client.POSTFIELDS, post_data)
    buffer = BytesIO()
    client.setopt(client.WRITEDATA, buffer)
    client.setopt(pycurl.USERAGENT, "BeruskaApp/1.2 (+tomas.vlasaty8@gmail.cz; https://jomipon-beruska-prototyp.streamlit.app/)")
    if headers is not None and len(headers) > 0:
        client.setopt(pycurl.HTTPHEADER, headers)
    client.perform()
    status_code = client.getinfo(pycurl.RESPONSE_CODE)
    if status_code != 200:
        return ""
    client.close()
    body = buffer.getvalue()
    return body
    """
    client = pycurl.Curl()
    client.setopt(pycurl.URL, url)
    buffer = BytesIO()
    client.setopt(client.WRITEDATA, buffer)
    client.setopt(pycurl.USERAGENT, "BeruskaApp/1.2 (+tomas.vlasaty8@gmail.cz; https://jomipon-beruska-prototyp.streamlit.app/)")
    if headers is not None and len(headers) > 0:
        client.setopt(pycurl.HTTPHEADER, headers)
    client.setopt(pycurl.POST, 1)
    client.setopt(pycurl.TIMEOUT_MS, 3000)
    client.perform()
    status_code = client.getinfo(pycurl.RESPONSE_CODE)
    if status_code != 200:
        return ""
    client.close()
    body = buffer.getvalue()
    #return body
    """

def download_post_url_2(url, post_data, headers):
    if post_data.strip().startswith("{") or post_data.strip().startswith("["):
        post_data = (
            post_data
            .replace(": True", ": true")
            .replace(": False", ": false")
            .replace(": None", ": null")
        )
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    #curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json'])
    if headers is not None and len(headers) > 0:
        curl.setopt(pycurl.HTTPHEADER, headers)
    curl.setopt(pycurl.POST, 1)

    # If you want to set a total timeout, say, 3 seconds
    curl.setopt(pycurl.TIMEOUT_MS, 3000)

    ## depending on whether you want to print details on stdout, uncomment either
    # curl.setopt(pycurl.VERBOSE, 1) # to print entire request flow
    ## or
    # curl.setopt(pycurl.WRITEFUNCTION, lambda x: None) # to keep stdout clean

    # preparing body the way pycurl.READDATA wants it
    # NOTE: you may reuse curl object setup at this point
    #  if sending POST repeatedly to the url. It will reuse
    #  the connection.
    #body_as_dict = {"name": "abc", "path": "def", "target": "ghi"}
    #body_as_json_string = json.dumps(body_as_dict) # dict to json
    body_as_file_object = StringIO(post_data)
    buffer = BytesIO()
    curl.setopt(pycurl.WRITEDATA, buffer)
    # prepare and send. See also: pycurl.READFUNCTION to pass function instead
    curl.setopt(pycurl.READDATA, body_as_file_object)
    curl.setopt(pycurl.POSTFIELDSIZE, len(post_data))
    curl.perform()

    # you may want to check HTTP response code, e.g.
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)

    # don't forget to release connection when finished
    curl.close()
    body_responce = buffer.getvalue()
    return body_responce
def download_post_url_3(url, post_data, headers):
    if post_data.strip().startswith("{") or post_data.strip().startswith("["):
        post_data = (
            post_data
            .replace(": True", ": true")
            .replace(": False", ": false")
            .replace(": None", ": null")
        )
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    #curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json'])
    if headers is not None and len(headers) > 0:
        curl.setopt(pycurl.HTTPHEADER, headers)
    curl.setopt(pycurl.POST, 1)

    # If you want to set a total timeout, say, 3 seconds
    curl.setopt(pycurl.TIMEOUT_MS, 3000)

    ## depending on whether you want to print details on stdout, uncomment either
    # curl.setopt(pycurl.VERBOSE, 1) # to print entire request flow
    ## or
    # curl.setopt(pycurl.WRITEFUNCTION, lambda x: None) # to keep stdout clean

    # preparing body the way pycurl.READDATA wants it
    # NOTE: you may reuse curl object setup at this point
    #  if sending POST repeatedly to the url. It will reuse
    #  the connection.
    #body_as_dict = {"name": "abc", "path": "def", "target": "ghi"}
    #body_as_json_string = json.dumps(body_as_dict) # dict to json
    body_as_file_object = StringIO(post_data)
    buffer = BytesIO()
    curl.setopt(pycurl.WRITEDATA, buffer)
    # prepare and send. See also: pycurl.READFUNCTION to pass function instead
    curl.setopt(pycurl.READDATA, body_as_file_object)
    curl.setopt(pycurl.POSTFIELDSIZE, len(post_data))
    curl.perform()

    # you may want to check HTTP response code, e.g.
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)

    # don't forget to release connection when finished
    curl.close()
    body_responce = buffer.getvalue()
    return body_responce
def download_post_url_4(url, post_data, headers):
    if post_data.strip().startswith("{") or post_data.strip().startswith("["):
        post_data = (
            post_data
            .replace(": True", ": true")
            .replace(": False", ": false")
            .replace(": None", ": null")
        )
    buffer = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    if headers is not None and len(headers) > 0:
        c.setopt(pycurl.HTTPHEADER, headers)
    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    response = buffer.getvalue()
    return response
def download_put_url(url, post_data, headers):
    if post_data.strip().startswith("{") or post_data.strip().startswith("["):
        post_data = (
            post_data
            .replace(": True", ": true")
            .replace(": False", ": false")
            .replace(": None", ": null")
        )
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    #curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json'])
    if headers is not None and len(headers) > 0:
        curl.setopt(pycurl.HTTPHEADER, headers)
    curl.setopt(pycurl.PUT, 1)

    # If you want to set a total timeout, say, 3 seconds
    curl.setopt(pycurl.TIMEOUT_MS, 3000)

    ## depending on whether you want to print details on stdout, uncomment either
    # curl.setopt(pycurl.VERBOSE, 1) # to print entire request flow
    ## or
    # curl.setopt(pycurl.WRITEFUNCTION, lambda x: None) # to keep stdout clean

    # preparing body the way pycurl.READDATA wants it
    # NOTE: you may reuse curl object setup at this point
    #  if sending POST repeatedly to the url. It will reuse
    #  the connection.
    #body_as_dict = {"name": "abc", "path": "def", "target": "ghi"}
    #body_as_json_string = json.dumps(body_as_dict) # dict to json
    body_as_file_object = StringIO(post_data)
    buffer = BytesIO()
    curl.setopt(pycurl.WRITEDATA, buffer)
    # prepare and send. See also: pycurl.READFUNCTION to pass function instead
    curl.setopt(pycurl.READDATA, body_as_file_object)
    curl.setopt(pycurl.POSTFIELDSIZE, len(post_data))
    curl.perform()

    # you may want to check HTTP response code, e.g.
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)

    # don't forget to release connection when finished
    curl.close()
    body_responce = buffer.getvalue()
    return body_responce

def download_delete_url(url, headers):
    client = pycurl.Curl()
    client.setopt(pycurl.URL, url)
    buffer = BytesIO()
    client.setopt(pycurl.WRITEDATA, buffer)
    #client.setopt(pycurl.DELETE, 1)
    client.setopt(pycurl.CUSTOMREQUEST, "DELETE")
    client.setopt(pycurl.USERAGENT, "BeruskaApp/1.2 (+tomas.vlasaty8@gmail.cz; https://jomipon-beruska-prototyp.streamlit.app/)")
    if headers is not None and len(headers) > 0:
        client.setopt(pycurl.HTTPHEADER, headers)
    client.perform()
    status_code = client.getinfo(pycurl.RESPONSE_CODE)
    if status_code != 200:
        return ""
    client.close()
    body = buffer.getvalue()
    return body

def remove_diacriticism(name):
    chars_replace = [ ["á","a"], ["é","e"], ["í","i"], ["ó","o"], ["ú","u"], ["ů","u"], ["ý","y"], ["č","c"], ["ď","d"], ["ě","e"], ["ň","n"], ["š","s"], ["ť","t"], ["ž","z"], ["ř","r"] ]
    for char_replace in chars_replace:
        name = name.replace(char_replace[0], char_replace[1])
    return name

def call_create_owner_api(fast_api_url_base, access_token):
    """
    zavolá create_owner_id propřípravu tabulek
    """
    url = f"{fast_api_url_base}/create_owner_id"
    body = download_get_url(url, [f"Authorization: Bearer {access_token}"])
    body = body.decode('UTF-8')
    return body

def get_access_token(refresh_token):
    """
    Stáhnout nový access tokoen pomocí refresh tokenu
    """
    fast_api_url_base = os.getenv("FAST_API_URL_BASE")
    fast_api_url_refresh = os.getenv("FAST_API_URL_REFRESH")
    url = f"{fast_api_url_base}{fast_api_url_refresh}"
    body = download_get_url(url.format(refresh_token = refresh_token), ())
    body = body.decode('UTF-8')
    user_data = json.loads(body)
    access_token_new = user_data["access_token"]
    return access_token_new

def get_changes(old, new, path=()):
    """"
    Vrací seznam změn
    """
    changes = {}
    if isinstance(old, dict) and isinstance(new, dict):
        keys = set(old) | set(old)
        for key in keys:
            p = path + (key,)
            if key not in old:
                changes[p] = new[key]
            elif key not in new:
                changes[p] = None
            else:
                sub = get_changes(old[key], new[key], p)
                changes.update(sub)
    elif old != new:
        changes[path] = new
    return changes
