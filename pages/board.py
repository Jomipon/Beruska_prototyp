import streamlit as st
from login import get_session_from_session_state, set_session_from_params, get_session_from_cookies
from support import download_get_url
from forecast import forecast

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k databázi")
    #st.switch_page("pages/board.py")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = st.session_state["cookies"]
set_session_from_params(st.session_state["sb_database"])
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if database is None:
    st.stop()

if session:
    settings = database.from_("settings").select("*").execute()
    if settings.data:
        if settings.data[0]["weather_enable"] and settings.data[0]["weather_lat"] and settings.data[0]["weather_lon"]:
            lat = settings.data[0]["weather_lat"]
            lon = settings.data[0]["weather_lon"]
            weather = forecast(lat,lon)
            xml_data = weather.download_data()
            pd_data = weather.parse_download_data(xml_data)
            if len(pd_data) > 0:
                weatner_picture = weather.create_graf(pd_data)
                st.write("Předpověď počasí na další dny")
                st.image(weatner_picture)
