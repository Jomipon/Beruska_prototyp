import streamlit as st
from login import get_session_from_session_state
from copy import deepcopy


if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.query_params.clear() 
    st.switch_page("pages/board.py")

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

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

st.markdown("**Nastavení**")
    
if settings:
    st.session_state[f"settings_orig"] = settings
    settings_edited = deepcopy(st.session_state[f"settings_orig"])
    with st.container(border=True):
        settings_edited["weather_enable"] = st.checkbox("Předpověď počasí:", settings_edited["weather_enable"])
        if settings_edited["weather_enable"] == 0:
            settings_edited["weather_place"] = st.text_input("Město:", settings_edited["weather_place"])
        else:
            settings_edited["weather_place"] = st.text_input("Město:", settings_edited["weather_place"])
        
        settings_edited["quote_enable"] = st.checkbox("Moudro dne:", settings_edited["quote_enable"])

    if st.button("Uložit"):
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

    



