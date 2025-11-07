import pycurl
from io import BytesIO


def download_get_url(url):
    client = pycurl.Curl()
    client.setopt(client.URL, url)
    buffer = BytesIO()
    client.setopt(client.WRITEDATA, buffer)
    ## Setup SSL certificates
    #c.setopt(c.CAINFO, certifi.where())
    ## Make Request
    client.perform()
    ## Response Status Code
    #st.write('Response Code:', client.getinfo(client.RESPONSE_CODE))
    ## Final URL
    #st.write('Response URL:', client.getinfo(client.EFFECTIVE_URL))
    ## Cert Info
    #st.write('Response Cert Info:', client.getinfo(client.INFO_CERTINFO))
    ## Close Connection
    client.close()

    ## Retrieve the content BytesIO & Decode
    body = buffer.getvalue()
    return body

def remove_diacriticism(name):
    chars_replace = [ ["á","a"], ["é","e"], ["í","i"], ["ó","o"], ["ú","u"], ["ů","u"], ["ý","y"], ["č","c"], ["ď","d"], ["ě","e"], ["ň","n"], ["š","s"], ["ť","t"], ["ž","z"], ["ř","r"] ]
    for char_replace in chars_replace:
        name = name.replace(char_replace[0], char_replace[1])
    return name
