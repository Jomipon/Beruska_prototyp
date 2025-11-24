#Tvorba výdejky
from login import get_session_from_session_state
import streamlit as st
from copy import deepcopy
import uuid
import datetime

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

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

st.write("Tvorba výdejky")

issue_id = st.query_params.get("id", None)
is_new = st.query_params.get("new", "0")
is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
if is_new and not issue_id:
    issue_id = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.query_params["id"] = issue_id
if not issue_id:
    st.query_params.clear() 
    st.switch_page("pages/store/issue/issues.py")
else:
    try:
        issue_head = database.from_("issue_head").select("*, company(*)").filter("issue_id", "eq", str(issue_id)).execute()
        st.write(f"{issue_head=}")
    except:
        st.query_params.clear() 
        st.switch_page("pages/board.py")
    if issue_head.data:
        #edit
        issue_head = issue_head.data[0]
        if is_new:
            st.query_params.pop("new")
            is_new = 0
    else:
        #new
        if is_new:
            issue_head = {
                "issue_id": issue_id,
                "issue_number": "",
                "date_of_issue": datetime.date.today(),
                "company_id": None,
                "note": "",
                "place": "",
                "issue_price": 0,
            }
        else:
            st.query_params.clear() 
            st.switch_page("pages/store/issue/issues.py")

def check_before_save(checked_issue):
    result = True
    if not checked_issue["issue_number"] or len(checked_issue["issue_number"]) == 0:
        st.error("Není vyplněné číslo dokladu")
        result = False
    elif not checked_issue["date_of_issue"]:
        st.error("Není vyplněný datum výdeje")
        result = False
    return result
    
columns_issue_head = [
                "issue_number", 
                "date_of_issue", 
                "company_id", 
                "note", 
                "place", 
                "issue_price"
                ]
if is_new:
    st.markdown("**Nová výdejka**")
else:
    st.markdown("**Detail výdejky**")
if issue_head:
    if f"issue_head_orig_{issue_id}" not in st.session_state:
        st.session_state[f"issue_head_orig_{issue_id}"] = issue_head
        for column_issue_head in columns_issue_head:
            if column_issue_head not in st.session_state:
                if column_issue_head == "date_of_issue" and issue_head[column_issue_head] is not None:
                    st.session_state[f"issue_head_{issue_id}_{column_issue_head}"] = datetime.datetime.strptime(issue_head[column_issue_head], "%Y-%m-%d").date()
                else:
                    st.session_state[f"issue_head_{issue_id}_{column_issue_head}"] = issue_head[column_issue_head]
    
    st.text_input("Číslo dokladu:", key=f"issue_head_{issue_id}_issue_number", disabled=(is_new==0))
    st.date_input("Datum vydání:", key=f"issue_head_{issue_id}_date_of_issue", disabled=(is_new==0))
    st.text_input("Společnost:", key=f"issue_head_{issue_id}_company_id", disabled=(is_new==0))
    st.text_input("Poznámka:", key=f"issue_head_{issue_id}_note", disabled=(is_new==0))
    st.text_input("Místo:", key=f"issue_head_{issue_id}_place", disabled=(is_new==0))
    #st.text_input("Celková částka:", key=f"issue_head_{issue_id}_issue_price")

    issue_head_edited = deepcopy(st.session_state[f"issue_head_orig_{issue_id}"])
    for column_issue_head in columns_issue_head:
        issue_head_edited[column_issue_head] = st.session_state[f"issue_head_{issue_id}_{column_issue_head}"]
    if is_new:
        if st.button("Vytvořit") and check_before_save(issue_head_edited):
            insert_data = {
                "issue_id": issue_id
            }
            insert_data = {}
            for column_name in columns_issue_head:
                if isinstance(issue_head_edited[column_name], datetime.date):
                    insert_data[column_name] = issue_head_edited[column_name].strftime("%Y-%m-%d")
                else:
                    insert_data[column_name] = issue_head_edited[column_name]
            insert_data["issue_id"] = issue_id
            try:
                database.from_("issue_head").insert(insert_data).execute()
                st.session_state.pop(f"issue_head_orig_{issue_id}")
                st.query_params.pop("new", None)
                st.success("Vytvořeno")
                st.toast("Výdejka byla vytvořena", icon="✅")
                #st.switch_page("pages/store/assortment/assortments.py")
            except Exception as E:
                st.error("Nepovedlo se vytvořit výdejku")
                st.error(E)
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Uložit") and check_before_save(issue_head_edited):
                changes = get_changes(st.session_state[f"issue_head_orig_{issue_id}"], issue_head_edited, ())
                changes = {".".join(k): v for k, v in changes.items()}
                changes = {k: v for k, v in changes.items() if k}
                if not changes:
                    st.write("Nebylo co uložit")
                else:
                    try:
                        updated_data = database.from_("issue_head").update(changes).eq("issue_id", issue_id).execute()
                        st.session_state.pop(f"issue_head_orig_{issue_id}")
                        st.query_params.pop("new", None)
                        st.success("Uloženo")
                        st.toast("Výdejka byla uložena", icon="✅")
                    except:
                        st.error("Nepovedlo se uložit data")
