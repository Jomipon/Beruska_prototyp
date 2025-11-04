from login import get_session_from_session_state
import streamlit as st
from copy import deepcopy
import uuid
import datetime


if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.stop()
    #st.switch_page("pages/board.py")

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

person_types = {
    0: "Fyzická osoba",
    1: "Právnická osoba"
}
relationship_types = {
    0: "Odběratel",
    1: "Dodavatel",
    2: "Dodavatel + Odběratel"
}

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
id_company = st.query_params.get("id", None)
is_new = st.query_params.get("new", "0")
is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
if is_new and not id_company:
    id_company = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.query_params["id"] = id_company
if not id_company:
    st.query_params.clear() 
    st.switch_page("/company//companies.py")
else:
    try:
        company = database.from_("company").select("*").filter("company_id", "eq", str(id_company)).execute()
    except:
        st.query_params.clear() 
        st.switch_page("pages/board.py")
    if company.data:
        #edit
        company = company.data[0]
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
                db.from_("company").delete().eq("company_id", company_id).execute()
                st.toast(f"Partner byl smazan", icon="✅")
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
    company_edited = deepcopy(st.session_state[f"company_orig_{id_company}"])
    with st.container(border=True):
        company_edited["type_person"] = st.radio("Typ osoby:", 
                                                 options=list(person_types.keys()), 
                                                 index=list(person_types.keys()).index(company_edited["type_person"]), 
                                                 horizontal=True,  
                                                 format_func=lambda k: person_types[k], 
                                                 key=f"type_{id_company}")
        if company_edited["type_person"] == 0:
            company_edited["name_first"] = st.text_input("Jméno:", company_edited["name_first"])
            company_edited["name_last"] = st.text_input("Příjmení:", company_edited["name_last"])
        else:
            company_edited["name"] = st.text_input("Název:", company_edited["name"])
            company_edited["ico"] = st.text_input("IČO:", company_edited["ico"])
    company_edited["active"] = st.checkbox("Aktivní:", company_edited["active"])
    company_edited["note"] = st.text_input("Poznámka:", company_edited["note"])
    company_edited["address"] = st.text_input("Adresa:", company_edited["address"])
    company_edited["email"] = st.text_input("Email:", company_edited["email"])
    company_edited["phone_number"] = st.text_input("Telefon:", company_edited["phone_number"])
    company_edited["alias"] = st.text_input("Alias:", company_edited["alias"])
    company_edited["type_relationship"] = st.radio("Vztah:", 
                                                options=list(relationship_types.keys()), 
                                                index=list(relationship_types.keys()).index(company_edited["type_relationship"]), 
                                                horizontal=True,  
                                                format_func=lambda k: relationship_types[k], 
                                                key=f"relationship_{id_company}")
    if is_new:
        if st.button("Vytvořit"):
            insert_data = {
                "company_id":id_company
            }
            insert_data = {}
            for column_name in company_columns:
                insert_data[column_name] = company_edited[column_name]
            insert_data["company_id"] = id_company
            try:
                database.from_("company").insert(insert_data).execute()
                st.query_params.pop("new", None)
                st.success("Vytvořeno")
                st.toast("Partner byl vytvořen", icon="✅")
                st.switch_page("pages/company/companies.py")
            except Exception as E:
                st.error("Nepovedlo se vytvořit partnera")
                st.error(E)

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Uložit"):
                changes = get_changes(st.session_state[f"company_orig_{id_company}"], company_edited, ())
                changes = {".".join(k): v for k, v in changes.items()}
                changes = {k: v for k, v in changes.items() if k}
                if not changes:
                    st.write("Nebylo co uložit")
                else:
                    try:
                        updated_data = database.from_("company").update(changes).eq("company_id", id_company).execute()
                        st.query_params.pop("new", None)
                        st.success("Uloženo")
                        st.toast("Partner byl uložen", icon="✅")
                    except:
                        st.error("Nepovedlo se uložit data")
        with col2:
            if st.button("Smazat"):
                company_name = f'{company_edited["name_first"]} {company_edited["name_last"]}' if company_edited["type_person"] == 0 else company_edited["name"]
                partner_smazat(database, id_company, company_name)
