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

item_types = {
    0: "Sortiment",
    1: "Služba"
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
id_item = st.query_params.get("id", None)
is_new = st.query_params.get("new", "0")
is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
if is_new and not id_item:
    id_item = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.query_params["id"] = id_item
if not id_item:
    st.query_params.clear() 
    st.switch_page("pages/assortment/assortments.py")
else:
    try:
        item = database.from_("item").select("*").filter("item_id", "eq", str(id_item)).execute()
    except:
        st.query_params.clear() 
        st.switch_page("pages/board.py")
    if item.data:
        #edit
        item = item.data[0]
        if is_new:
            st.query_params.pop("new")
            is_new = 0
    else:
        #new
        if is_new:
            item = {
                "item_id": id_item,
                "owner_id": None, 
                "name": "", 
                "price_purchase": 0,
                "price_selling": 0,
                "item_type": 0,
                "active": True,
                "note": "",
                "created_at": None,
            }
        else:
            st.query_params.clear() 
            st.switch_page("pages/assortment/assortments.py")

@st.dialog("Smazat sortiment")
def sortiment_smazat(db, item_id, item_name):
    st.write("Opravdu chcete smazat sortiment?")
    st.write(f"{item_name}")
    st.write(f"({item_id})")
    col_smazat, col_konec = st.columns(2)
    with col_smazat:
        if st.button("Smazat"):
            zavrit_dialog = False
            try:
                db.from_("item").delete().eq("item_id", item_id).execute()
                st.toast(f"Sortiment byl smazan", icon="✅")
                zavrit_dialog = True
            except Exception as e:
                st.error("Nepovedlo se smazat sortiment")
                st.error(e)
            if zavrit_dialog:
                st.rerun()
    with col_konec:
        if st.button("Zavřít"):
            st.rerun()
def check_before_save(checked_item):
    result = True
    if not checked_item["name"] or len(checked_item["name"]) == 0:
        st.error("Není vyplněný název sortimentu")
        result = False
    elif not checked_item["price_purchase"]:
        st.error("Není vyplněná nákupní cena")
        result = False
    elif not checked_item["price_selling"]:
        st.error("Není vyplněná prodejní cena")
        result = False
    return result
    

item_columns = [
                "item_id",
                "name",
                "price_purchase",
                "price_selling",
                "item_type",
                "active",
                "note"
                ]
if is_new:
    st.markdown("**Nový sortiment**")
else:
    st.markdown("**Detail sortimentu**")
if item:
    st.session_state[f"item_orig_{id_item}"] = item
    item_edited = deepcopy(st.session_state[f"item_orig_{id_item}"])
    item_edited["item_type"] = st.radio("Typ sortimentu:", 
                                                options=list(item_types.keys()), 
                                                index=list(item_types.keys()).index(item_edited["item_type"]), 
                                                horizontal=True,  
                                                format_func=lambda k: item_types[k], 
                                                key=f"type_{id_item}")
    item_edited["active"] = st.checkbox("Aktivní:", item_edited["active"])
    item_edited["name"] = st.text_input("Název:", item_edited["name"])
    #item_edited["price_purchase"] = st.text_input("Nákupní cena:", item_edited["price_purchase"])
    st.number_input("Nákupní cena", min_value=0, value=item_edited["price_purchase"], step=1)
    st.number_input("Prodejní cena", min_value=0, value=item_edited["price_selling"], step=1)
    item_edited["note"] = st.text_input("Poznámka:", item_edited["note"])
    if is_new:
        if st.button("Vytvořit") and check_before_save(item_edited):
            insert_data = {
                "item_id":id_item
            }
            insert_data = {}
            for column_name in item_columns:
                insert_data[column_name] = item_edited[column_name]
            insert_data["item_id"] = id_item
            try:
                database.from_("item").insert(insert_data).execute()
                st.query_params.pop("new", None)
                st.success("Vytvořeno")
                st.toast("Sortiment byl vytvořen", icon="✅")
                st.switch_page("pages/assortment/assortments.py")
            except Exception as E:
                st.error("Nepovedlo se vytvořit sortiment")
                st.error(E)

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Uložit") and check_before_save(item_edited):
                changes = get_changes(st.session_state[f"item_orig_{id_item}"], item_edited, ())
                changes = {".".join(k): v for k, v in changes.items()}
                changes = {k: v for k, v in changes.items() if k}
                if not changes:
                    st.write("Nebylo co uložit")
                else:
                    try:
                        updated_data = database.from_("item").update(changes).eq("item_id", id_item).execute()
                        st.query_params.pop("new", None)
                        st.success("Uloženo")
                        st.toast("Sortiment byl uložen", icon="✅")
                    except:
                        st.error("Nepovedlo se uložit data")
        with col2:
            if st.button("Smazat"):
                sortiment_smazat(database, id_item, item_edited["name"])
