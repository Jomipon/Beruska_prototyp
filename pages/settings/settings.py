import streamlit as st
from login import get_session_from_session_state, set_session_from_params, get_session_from_cookies
from copy import deepcopy
import xml.etree.ElementTree as ET
from support import download_get_url, remove_diacriticism

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.query_params.clear() 
    st.switch_page("pages/board.py")

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = st.session_state["cookies"]
set_session_from_params(st.session_state["sb_database"])
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

columns_settings = ["weather_enable", "weather_place", "weather_lat", "weather_lon", "quote_enable"]

if database is None:
    st.query_params.clear() 
    st.switch_page("pages/board.py")

try:
    database.rpc("create_owner_id").execute()
except:
    st.query_params.clear() 
    st.switch_page("pages/board.py")

def get_changes(old, new, path=()):
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

try:
    database.rpc("create_owner_id").execute()
    settings = database.from_("settings").select("*").execute()
except:
    st.query_params.clear() 
    st.switch_page("pages/board.py")
if settings.data:
    #edit
    settings = settings.data[0]

def check_before_save(checked_item):
    result = True
    if checked_item["weather_enable"]:
        if not checked_item["weather_place"]:
            st.error("Nevyplněné místo pro předpověď počasí")
            result = False
    return result

def get_gps_from_xml(xml):
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
def get_place_location(place_name, database):
    settings = database.from_("weather_place").select("*").filter("place_name", "eq", place_name.lower()).execute()
    lat = 0
    lng = 0
    if len(settings.data) == 0:
        place_name_goolge = place_name.lower()
        place_name_goolge = remove_diacriticism(place_name_goolge)
        url = f"https://maps.googleapis.com/maps/api/geocode/xml?address={place_name_goolge}&key=AIzaSyDf1xnPM2PTDowuBpaPBZS5tczenG9rN3g"
        body = download_get_url(url)
        body = body.decode('UTF-8')
        lat, lng = get_gps_from_xml(body)
        insert_data = {
            "place_name": place_name.lower(),
            "place_lat": lat,
            "place_lon": lng
        }
        database.from_("weather_place").insert(insert_data).execute()
    else:
        lat = settings.data[0]["place_lat"]
        lng = settings.data[0]["place_lon"]
    return (lat, lng)

st.markdown("**Nastavení**")

if settings:
    st.session_state[f"settings_orig"] = settings
    for column_settings in columns_settings:
        if column_settings not in st.session_state:
            st.session_state[column_settings] = settings[column_settings]

    st.checkbox("Předpověď počasí:", key="weather_enable")
    st.text_input("Město:", key="weather_place", disabled=st.session_state.weather_enable == 0)
    col_convert, col_lan, col_lon = st.columns(3)
    with col_convert:
        if st.button("Převest na souřadnice"):
            if not st.session_state.weather_place:
                st.error("Není vyplněná oblast")
            else:
                lat, lon = get_place_location(st.session_state.weather_place, database)
                if lat and lon:
                    st.session_state.weather_lat = lat
                    st.session_state.weather_lon = lon

    with col_lan:
        st.number_input("Lat:", key="weather_lat")
    with col_lon:
        st.number_input("Lon:", key="weather_lon")

    st.checkbox("Zobrazit moudro dne:", key="quote_enable")
    settings_edited = deepcopy(st.session_state[f"settings_orig"])
    for column_settings in columns_settings:
        settings_edited[column_settings] = st.session_state[column_settings]
    if st.button("Uložit") and check_before_save(settings_edited):
        changes = get_changes(st.session_state[f"settings_orig"], settings_edited, ())
        changes = {".".join(k): v for k, v in changes.items()}
        changes = {k: v for k, v in changes.items() if k}
        if not changes:
            st.write("Nebylo co uložit")
        else:
            try:
                owner_id = database.rpc("get_owner_id").execute()
                updated_data = database.from_("settings").update(changes).eq("owner_id", owner_id.data).execute()
                st.success("Uloženo")
            except Exception as e:
                st.error("Nepovedlo se uložit data")
                st.error(e)

    



