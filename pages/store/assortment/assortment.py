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
    Hlavní metoda pro zobrazení detailu sortimentu
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
    fast_api_url_item_c = os.getenv("FAST_API_URL_ITEM_C")
    fast_api_url_item_rud = os.getenv("FAST_API_URL_ITEM_RUD")
    refresh_token = session.refresh_token

    if database is None:
        st.stop()

    try:
        access_token_new = get_access_token(refresh_token)
        
        call_create_owner_api(fast_api_url_base, access_token_new)
    except Exception:
        st.query_params.clear()
        st.stop()

    item_types = {
        0: "Sortiment",
        1: "Služba"
    }

    id_item = st.query_params.get("id", None)
    is_new = st.query_params.get("new", "0")
    is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
    if is_new and not id_item:
        id_item = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        st.query_params["id"] = id_item
    if not id_item:
        st.query_params.clear() 
        st.switch_page("pages/store/assortment/assortments.py")
    else:
        try:
            url = f"{fast_api_url_base}{fast_api_url_item_rud.format(item_id=id_item)}"
            body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
            body = body.decode('UTF-8')
            item = json.loads(body)
        except:
            st.query_params.clear() 
            st.switch_page("pages/board.py")
        if "item_id" in item:
            #edit
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
                    "item_number": "",
                    "price_purchase": 0,
                    "price_selling": 0,
                    "item_type": 0,
                    "active": True,
                    "note": "",
                    "created_at": None,
                }
            else:
                st.query_params.clear() 
                st.switch_page("pages/store/assortment/assortments.py")

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
                    url = f"{fast_api_url_base}{fast_api_url_item_rud}".format(item_id=id_item)
                    body = download_delete_url(url, [f"Authorization: Bearer {access_token_new}"])
                    ins_responce = json.loads(body)
                    #db.from_("item").delete().eq("item_id", item_id).execute()
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
    
    columns_item = [
                    "item_id",
                    "name",
                    "price_purchase",
                    "price_selling",
                    "item_type",
                    "active",
                    "note",
                    "item_number"
                    ]
    if is_new:
        st.markdown("**Nový sortiment**")
    else:
        st.markdown("**Detail sortimentu**")
    if item:
        if f"item_orig_{id_item}" not in st.session_state:
            st.session_state[f"item_orig_{id_item}"] = item
            for column_item in columns_item:
                if column_item not in st.session_state:
                    st.session_state[f"item_{id_item}_{column_item}"] = item[column_item]
        st.radio("Typ sortimentu:", 
                    options=list(item_types.keys()),
                    index=list(item_types.keys()).index(st.session_state[f"item_{id_item}_item_type"]),
                    horizontal=True,
                    format_func=lambda k: item_types[k],
                    key=f"item_{id_item}_item_type")
        st.checkbox("Aktivní:", key=f"item_{id_item}_active")
        st.text_input("Název:", key=f"item_{id_item}_name")
        st.text_input("Číslo:", key=f"item_{id_item}_item_number")
        #item_edited["price_purchase"] = st.text_input("Nákupní cena:", item_edited["price_purchase"])
        st.number_input("Nákupní cena", min_value=0, key=f"item_{id_item}_price_purchase", step=1)
        st.number_input("Prodejní cena", min_value=0, key=f"item_{id_item}_price_selling", step=1)
        st.text_input("Poznámka:", key=f"item_{id_item}_note")
        item_edited = deepcopy(st.session_state[f"item_orig_{id_item}"])
        for column_item in columns_item:
            item_edited[column_item] = st.session_state[f"item_{id_item}_{column_item}"]
        if is_new:
            if st.button("Vytvořit") and check_before_save(item_edited):
                insert_data = {
                    "item_id":id_item
                }
                insert_data = {}
                for column_name in columns_item:
                    insert_data[column_name] = item_edited[column_name]
                insert_data["item_id"] = id_item
                try:
                    url = f"{fast_api_url_base}{fast_api_url_item_c}"
                    body = download_post_url(url, json.dumps(item_edited), [f"Authorization: Bearer {access_token_new}","Content-Type: application/json"])
                    #database.from_("item").insert(insert_data).execute()
                    st.session_state.pop(f"item_orig_{id_item}")
                    st.query_params.pop("new", None)
                    st.success("Vytvořeno")
                    st.toast("Sortiment byl vytvořen", icon="✅")
                    #st.switch_page("pages/store/assortment/assortments.py")
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
                            #updated_data = database.from_("item").update(changes).eq("item_id", id_item).execute()
                            url = f"{fast_api_url_base}{fast_api_url_item_rud.format(item_id=id_item)}"
                            body = download_put_url(url, json.dumps(item_edited), [f"Authorization: Bearer {access_token_new}"])
                            ins_responce = json.loads(body)
                            st.session_state.pop(f"item_orig_{id_item}")
                            st.query_params.pop("new", None)
                            st.success("Uloženo")
                            st.toast("Sortiment byl uložen", icon="✅")
                        except:
                            st.error("Nepovedlo se uložit data")
            with col2:
                if st.button("Smazat"):
                    sortiment_smazat(database, id_item, item_edited["name"])

if __name__ == "__main__":
    main()
