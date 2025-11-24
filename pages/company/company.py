"""
Detail partnera
"""
from copy import deepcopy
import datetime
import json
import os
import uuid
from dotenv import load_dotenv
import streamlit as st
from login import get_session_from_session_state, get_session_from_cookies
from support import download_get_url, download_post_url, call_create_owner_api, get_access_token, get_changes, download_put_url, download_delete_url

def main():
    """
    Hlavní metoda pro zobrazení detailu partnera
    """
    load_dotenv()

    if "sb_database" not in st.session_state:
        st.error("Nepovedlo se připojit k databázi")
        st.stop()

    database = st.session_state.get("sb_database", None)

    session = None
    cookies = None
    session = None
    cookies = st.session_state["cookies"]
    session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
    session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

    if session is None:
        session = database.auth.get_session()
    fast_api_url_base = os.getenv("FAST_API_URL_BASE")
    fast_api_url_company_c = os.getenv("FAST_API_URL_COMPANY_C")
    fast_api_url_company_rud = os.getenv("FAST_API_URL_COMPANY_RUD")
    refresh_token = session.refresh_token

    if database is None:
        st.stop()

    try:
        access_token_new = get_access_token(refresh_token)
        
        call_create_owner_api(fast_api_url_base, access_token_new)
    except Exception:
        st.query_params.clear()
        st.stop()

    person_types = {
        0: "Fyzická osoba",
        1: "Právnická osoba"
    }
    relationship_types = {
        0: "Odběratel",
        1: "Dodavatel",
        2: "Dodavatel + Odběratel"
    }

    id_company = st.query_params.get("id", None)
    is_new = st.query_params.get("new", "0")
    is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
    if is_new and not id_company:
        id_company = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        st.query_params["id"] = id_company
    if not id_company:
        st.query_params.clear()
        st.switch_page("/company/companies.py")
    else:
        try:
            url = f"{fast_api_url_base}{fast_api_url_company_rud.format(company_id=id_company)}"
            body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
            body = body.decode('UTF-8')
            company = json.loads(body)
            #company = database.from_("company").select("*").filter("company_id", "eq", str(id_company)).execute()
        except Exception:
            st.query_params.clear()
            st.switch_page("pages/board.py")
        if "company_id" in company:
            #edit
            if is_new:
                st.query_params.pop("new")
                is_new = 0
        else:
            #new
            if is_new:
                company = {
                    "company_id":id_company, 
                    "owner_id": None, 
                    "name": "", 
                    "name_first": "", 
                    "name_last": "", 
                    "active": True, 
                    "note": "", 
                    "created_at":None, 
                    "type_person": 0,
                    "address": "",
                    "type_relationship": 0,
                    "email": "",
                    "phone_number": "",
                    "alias": "",
                    "foundation_id": "",
                    "ico": ""   
                    }
            else:
                st.query_params.clear()
                st.switch_page("pages/company/companies.py")

    @st.dialog("Smazat partnera")
    def partner_smazat(db, company_id, company_name):
        st.write("Opravdu chcete smazat partnera?")
        st.write(f"{company_name}")
        st.write(f"({company_id})")
        col_smazat, col_konec = st.columns(2)
        with col_smazat:
            if st.button("Smazat"):
                zavrit_dialog = False
                try:
                    #db.from_("company").delete().eq("company_id", company_id).execute()
                    url = f"{fast_api_url_base}{fast_api_url_company_rud}".format(company_id=company_id)
                    body = download_delete_url(url, [f"Authorization: Bearer {access_token_new}"])
                    ins_responce = json.loads(body)
                    st.toast("Partner byl smazan", icon="✅")
                    zavrit_dialog = True
                except Exception as e:
                    st.error("Nepovedlo se smazat partnera")
                    st.error(e)
                if zavrit_dialog:
                    st.rerun()
        with col_konec:
            if st.button("Zavřít"):
                st.rerun()
    company_columns = [
                    "company_id", 
                    "name", 
                    "name_first", 
                    "name_last", 
                    "active", 
                    "note", 
                    "type_person",
                    "address",
                    "type_relationship",
                    "email",
                    "phone_number",
                    "alias",
                    "foundation_id",
                    "ico"
                    ]
    if is_new:
        st.markdown("**Nový partner**")
    else:
        st.markdown("**Detail partnera**")
    if company:
        st.session_state[f"company_orig_{id_company}"] = company
        for company_column in company_columns:
            if f"{company_column}_{id_company}" not in st.session_state:
                st.session_state[f"{company_column}_{id_company}"] = company[company_column]

        with st.container(border=True):
            st.radio("Typ osoby:",
                    options=list(person_types.keys()),
                    index=list(person_types.keys()).index(st.session_state[f"type_person_{id_company}"]),
                    horizontal=True,
                    format_func=lambda k: person_types[k],
                    key=f"type_person_{id_company}")
            if st.session_state[f"type_person_{id_company}"] == 0:
                st.text_input("Jméno:", key=f"name_first_{id_company}")
                st.text_input("Příjmení:", key=f"name_last_{id_company}")
            else:
                st.text_input("Název:", key=f"name_{id_company}")
                st.text_input("IČO:", key=f"ico_{id_company}")
        st.checkbox("Aktivní:", key=f"active_{id_company}")
        st.text_input("Poznámka:", key=f"note_{id_company}")
        st.text_input("Adresa:", key=f"address_{id_company}")
        st.text_input("Email:", key=f"email_{id_company}")
        st.text_input("Telefon:", key=f"phone_number_{id_company}")
        st.text_input("Alias:", key=f"alias_{id_company}")
        st.radio("Vztah:",
            options=list(relationship_types.keys()),
            horizontal=True,
            format_func=lambda k: relationship_types[k],
            key=f"type_relationship_{id_company}")
        company_edited = deepcopy(st.session_state[f"company_orig_{id_company}"])
        company_edited = {}
        for company_column in company_columns:
            company_edited[company_column] = st.session_state[f"{company_column}_{id_company}"]
        if is_new:
            if st.button("Vytvořit"):
                try:
                    url = f"{fast_api_url_base}{fast_api_url_company_c}"
                    body = download_post_url(url, json.dumps(company_edited), [f"Authorization: Bearer {access_token_new}","Content-Type: application/json"])
                    ins_responce = json.loads(body)
                    st.query_params.pop("new", None)
                    st.success("Vytvořeno")
                    st.toast("Partner byl vytvořen", icon="✅")
                    #st.switch_page("pages/company/companies.py")
                except Exception as e:
                    st.error("Nepovedlo se vytvořit partnera")
                    st.error(e)
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Uložit"):
                    try:
                        #updated_data = database.from_("company").update(changes).eq("company_id", id_company).execute()
                        url = f"{fast_api_url_base}{fast_api_url_company_rud.format(company_id=id_company)}"
                        body = download_put_url(url, json.dumps(company_edited), [f"Authorization: Bearer {access_token_new}"])
                        ins_responce = json.loads(body)
                        st.query_params.pop("new", None)
                        st.success("Uloženo")
                        st.toast("Partner byl uložen", icon="✅")
                    except Exception as e:
                        st.error("Nepovedlo se uložit data")
                        st.error(e)
            with col2:
                if st.button("Smazat"):
                    company_name = f'{company_edited["name_first"]} {company_edited["name_last"]}' if company_edited["type_person"] == 0 else company_edited["name"]
                    partner_smazat(database, id_company, company_name)
if __name__ == "__main__":
    main()
    
