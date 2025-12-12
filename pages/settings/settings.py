from copy import deepcopy
import json
import os
import xml.etree.ElementTree as ET
import streamlit as st
from dotenv import load_dotenv
from login import get_session_from_session_state, get_session_from_cookies
from support import download_get_url, download_put_url, remove_diacriticism, call_create_owner_api, get_access_token, get_changes

def load_settings(refresh_token):
    """
    Stáhne nastavení z API
    """
    try:
        fast_api_url_base = os.getenv("FAST_API_URL_BASE")
        fast_api_url_settings = os.getenv("FAST_API_URL_SETTINGS")

        access_token_new = get_access_token(refresh_token)
        
        body = call_create_owner_api(access_token_new)
        
        url = f"{fast_api_url_base}{fast_api_url_settings}"
        body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
        settings = json.loads(body)
        return settings
    except Exception:
        st.query_params.clear()
        st.stop()
def check_before_save(checked_item):
    """
    Kontrola hodnot před uložením
    """
    result = True
    if checked_item["weather_enable"]:
        if not checked_item["weather_place"]:
            st.error("Nevyplněné místo pro předpověď počasí")
            result = False
    return result
def get_gps_from_xml(xml):
    """
    Vytažení GPS souřadnic z XML
    """
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    lat = 0
    lng = 0
    status = ""
    for child in root:
        if child.tag == "status":
            status = child.text
        if child.tag == "result":
            for child2 in child:
                if child2.tag == "geometry":
                    for child3 in child2:
                        if child3.tag == "location":
                            for child4 in child3:
                                if child4.tag == "lat":
                                    lat = child4.text
                                if child4.tag == "lng":
                                    lng = child4.text
    if status == "OK":
        lat = float(lat)
        lng = float(lng)
    return (lat, lng)
def get_place_location(place_name, access_token):
    """
    Vrátí GPS souiřadnice z názvu místa
    """
    #settings = database.from_("weather_place").select("*").filter("place_name", "eq", place_name.lower()).execute()
    fast_api_url_base = os.getenv("FAST_API_URL_BASE")
    fast_api_url_get_weather_place = os.getenv("FAST_API_URL_GET_WEATHER_PLACE")
    url = f"{fast_api_url_base}{fast_api_url_get_weather_place}".format(place_name=place_name)
    body = download_get_url(url, [f"Authorization: Bearer {access_token}"])
    weather_place = json.loads(body)
    lat = 0
    lng = 0
    if len(weather_place) > 0:
        lat = weather_place["place_lat"]
        lng = weather_place["place_lon"]
    return (lat, lng)

def main():
    """
    Hlavní metoda pro zobrazení nastavení
    """
    load_dotenv()

    if "sb_database" not in st.session_state:
        st.error("Nepovedlo se připojit k databázi")
        st.stop()

    database = st.session_state.get("sb_database", None)

    session = None
    cookies = st.session_state["cookies"]
    session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
    session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

    if session is None:
        session = database.auth.get_session()
    refresh_token = session.refresh_token

    if database is None:
        st.stop()

    columns_settings = ["weather_enable", "weather_place", "weather_lat", "weather_lon", "quote_enable"]

    fast_api_url_base = os.getenv("FAST_API_URL_BASE")
    fast_api_url_settings = os.getenv("FAST_API_URL_SETTINGS")
    
    access_token_new = get_access_token(refresh_token)
    call_create_owner_api(access_token_new)

    settings = load_settings(refresh_token)
    if settings:
        st.markdown("**Nastavení**")
        st.session_state["settings_orig"] = settings
        for column_settings in columns_settings:
            if column_settings not in st.session_state:
                st.session_state[column_settings] = settings[column_settings]

        st.checkbox("Předpověď počasí:", key="weather_enable")
        st.text_input("Město:", key="weather_place", disabled=st.session_state.weather_enable == 0)
        col_convert, col_lan, col_lon = st.columns(3)
        gps_actualize = False
        with col_convert:
            if st.button("Převest na souřadnice"):
                if not st.session_state.weather_place:
                    st.error("Není vyplněná oblast")
                else:
                    lat, lon = get_place_location(st.session_state.weather_place, access_token_new)
                    if lat and lon:
                        st.session_state.weather_lat = lat
                        st.session_state.weather_lon = lon
                        gps_actualize = True
        if gps_actualize:
            st.info("Souřadnice byla aktualizována")
        with col_lan:
            st.number_input("Lat:", key="weather_lat")
        with col_lon:
            st.number_input("Lon:", key="weather_lon")

        st.checkbox("Zobrazit moudro dne:", key="quote_enable")
        settings_edited = deepcopy(st.session_state["settings_orig"])
        for column_settings in columns_settings:
            settings_edited[column_settings] = st.session_state[column_settings]
        if st.button("Uložit") and check_before_save(settings_edited):
            url = f"{fast_api_url_base}{fast_api_url_settings}"
            body = download_put_url(url, json.dumps(settings_edited), [f"Authorization: Bearer {access_token_new}", "Content-Type: application/json"])
            ins_responce = json.loads(body)
            st.query_params.pop("new", None)
            st.success("Uloženo")
#                except Exception as e:
#                    st.error("Nepovedlo se uložit data")
#                    st.error(e)
if __name__ == "__main__":
    main()
