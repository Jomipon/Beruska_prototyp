import pycurl
from io import BytesIO
import streamlit as st

@st.cache_data
def download_get_url(url):
    client = pycurl.Curl()
    #client.setopt(client.URL, url)
    client.setopt(pycurl.URL, url.encode("utf-8"))
    buffer = BytesIO()
    client.setopt(client.WRITEDATA, buffer)
    client.setopt(pycurl.USERAGENT, "BeruskaApp/1.2 (+tomas.vlasaty8@gmail.cz; https://jomipon-beruska-prototyp.streamlit.app/)")
    # Volitelně debug:
    # client.setopt(pycurl.VERBOSE, True)
    client.perform()
    status = client.getinfo(pycurl.RESPONSE_CODE)
    client.close()
    body = buffer.getvalue()
    return body



def remove_diacriticism(name):
    chars_replace = [ ["á","a"], ["é","e"], ["í","i"], ["ó","o"], ["ú","u"], ["ů","u"], ["ý","y"], ["č","c"], ["ď","d"], ["ě","e"], ["ň","n"], ["š","s"], ["ť","t"], ["ž","z"], ["ř","r"] ]
    for char_replace in chars_replace:
        name = name.replace(char_replace[0], char_replace[1])
    return name
