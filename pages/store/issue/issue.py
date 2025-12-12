#Tvorba výdejky
import pandas as pd
from login import get_session_from_session_state, get_session_from_cookies
import os
from dotenv import load_dotenv
import json
import numpy as np
import streamlit as st
from copy import deepcopy
import uuid
import datetime
from support import download_get_url, call_create_owner_api, get_access_token, download_post_url, get_changes, call_create_issue_from_pre

def main():
    if "sb_database" not in st.session_state:
        st.error("Nepovedlo se připojit k adatabázi")
        st.stop()

    load_dotenv()

    database = st.session_state.get("sb_database", None)

    session = None
    cookies = None
    session = None
    cookies = st.session_state["cookies"]
    session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)
    session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

    if session is None:
        session = database.auth.get_session()
    if not session:
        return
    fast_api_url_base = os.getenv("FAST_API_URL_BASE")
    fast_api_url_issue_rud = os.getenv("FAST_API_URL_ISSUE_RUD")
    fast_api_url_issue_c = os.getenv("FAST_API_URL_ISSUE_C")
    fast_api_url_items = os.getenv("FAST_API_URL_ITEMS")
    
    refresh_token = session.refresh_token

    if database is None:
        st.stop()

    try:
        access_token_new = get_access_token(refresh_token)
        call_create_owner_api(access_token_new)
    except Exception as e:
        st.query_params.clear()
        st.stop()

    columns_issue_head = [
                    "issue_number", 
                    "date_of_issue", 
                    "company_id", 
                    "note", 
                    "place", 
                    "issue_price"
                    ]
    columns_issue_detail = [
                    "issue_id", 
                    "note", 
                    "item_id", 
                    "amoung", 
                    "price_peice", 
                    "price_row",
                    "item_name"
                    ]
    issue_id = st.query_params.get("id", None)
    is_new = st.query_params.get("new", "0")
    is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
    if is_new and not issue_id:
        issue_id = str(uuid.uuid4()).replace("-","")+datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        st.query_params["id"] = issue_id
    if not issue_id:
        st.query_params.clear()
        #st.switch_page("pages/store/issue/issues.py")
        st.stop()
    else:
        try:
            url = f"{fast_api_url_base}{fast_api_url_issue_rud.format(issue_id=issue_id)}"
            body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
            body = body.decode('UTF-8')
            issue_head = json.loads(body)
        except Exception as e:
            #st.query_params.clear()
            st.error(e)
            #st.switch_page("pages/board.py")
            st.stop()
        try:
            url = f"{fast_api_url_base}{fast_api_url_items}"
            body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
            body = body.decode('UTF-8')
            items = json.loads(body)
            items_filtered = [item["name"] for item in items if item["active"]]
            #items_filtered = []
            #for item in items:
            #    if item["active"]:
            #        items_filtered.append(item["name"])
        except Exception as e:
            #st.query_params.clear()
            #st.switch_page("pages/board.py")
            st.error(e)
            st.stop()
        if issue_head["data"]:
            #edit
            if is_new:
                st.query_params.pop("new")
                is_new = 0
        else:
            #new
            if is_new:
                issue_head = {
                    "status": "NEW",
                    "data": 
                    {
                        "issue_id": issue_id,
                        "issue_number": "",
                        "date_of_issue": datetime.date.today(),
                        "company_id": None,
                        "note": "",
                        "place": "",
                        "issue_price": 0,
                        "company": None
                    }
                }
                st.session_state["issue_details"] = pd.DataFrame(columns=columns_issue_detail, data=[])
            else:
                st.query_params.clear()
                st.stop()
                #st.switch_page("pages/store/issue/issues.py")

    def check_before_save(checked_issue):
        """
        Kontrola naplnění hodnot před ukládáním
        
        :param checked_issue: kontrolované hodnoty
        """
        result = True
        if not checked_issue["issue_number"] or len(checked_issue["issue_number"]) == 0:
            st.error("Není vyplněné číslo dokladu")
            result = False
        elif not checked_issue["date_of_issue"]:
            st.error("Není vyplněný datum výdeje")
            result = False
        return result

    if is_new:
        st.markdown("**Nová výdejka**")
    else:
        st.markdown("**Detail výdejky**")
    if issue_head["data"]:
        if f"issue_head_orig_{issue_id}" not in st.session_state:
            st.session_state[f"issue_head_orig_{issue_id}"] = issue_head["data"]
            for column_issue_head in columns_issue_head:
                if column_issue_head not in st.session_state:
                    if column_issue_head == "date_of_issue" and issue_head["data"][column_issue_head] is not None:
                        st.session_state[f"issue_head_{issue_id}_{column_issue_head}"] = datetime.date.today()
                    else:
                        st.session_state[f"issue_head_{issue_id}_{column_issue_head}"] = issue_head["data"][column_issue_head]
            st.session_state[f"issue_head_{issue_id}_company_name"] = ""
            if issue_head["data"]["company"] and issue_head["data"]["company"]["name"]:
                st.session_state[f"issue_head_{issue_id}_company_name"] = issue_head["data"]["company"]["name"]
        if "comapny_selected" in st.session_state:
            if st.session_state["comapny_selected"]['company_id'] is None:
                st.session_state[f"issue_head_{issue_id}_company_id"] = None
                st.session_state[f"issue_head_{issue_id}_company_name"] = ""
            else:
                st.session_state[f"issue_head_{issue_id}_company_id"] = st.session_state["comapny_selected"]['company_id']
                st.session_state[f"issue_head_{issue_id}_company_name"] = st.session_state["comapny_selected"]['name_full']
            st.session_state.pop("comapny_selected")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Číslo dokladu:", key=f"issue_head_{issue_id}_issue_number", disabled=(is_new==0))
            st.text_input("Poznámka:", key=f"issue_head_{issue_id}_note", disabled=(is_new==0))
        with col2:
            #st.text_input("Společnost:", key=f"issue_head_{issue_id}_company_id", disabled=(is_new==0))
            st.text_input("Společnost:", key=f"issue_head_{issue_id}_company_name", disabled=(is_new==0))
            @st.dialog("Výběr partnera")
            def partner_vyber(companies):
                st.write("Seznam partnerů")
                companies_data_editor = st.data_editor(
                    data=companies,
                    hide_index=True,
                        column_config={
                            "_pick": st.column_config.CheckboxColumn("Ozn.", width="small", disabled=False),
                            "company_id": st.column_config.TextColumn("ID Company", width="small", disabled=True),
                            "name_full": st.column_config.TextColumn("Název", width="small", disabled=True)
                        },
                        column_order=["_pick", "name_full"],
                        width="stretch",
                        key="companies_choose_editor"
                    )
                choose_company = None
                if companies_data_editor["_pick"].sum() > 0:
                    choose_company = companies_data_editor.where(companies_data_editor["_pick"] == 1).dropna(how="all").iloc[0]
                col_vlevo, col_vpravo = st.columns(2)
                with col_vlevo:
                    if st.button("Vybrat"):
                        if choose_company is None:
                            st.error("Není vybraný partner")
                        else:
                            st.session_state["comapny_selected"] = choose_company
                            st.rerun()
                with col_vpravo:
                    if st.button("Zavřít"):
                        st.rerun()

            if st.button("...", disabled=(is_new==0)):
                company_name = st.session_state[f"issue_head_{issue_id}_company_name"]
                company_id = st.session_state[f"issue_head_{issue_id}_company_id"]
                fast_api_url_companies = os.getenv("FAST_API_URL_COMPANIES")
                url = f"{fast_api_url_base}{fast_api_url_companies}"
                body = download_get_url(url, [f"Authorization: Bearer {access_token_new}"])
                body = body.decode('UTF-8')
                companies = json.loads(body)
                pd_companies = pd.DataFrame(companies)
                pd_companies = pd_companies[["company_id","name_full", "active"]]
                pd_companies = pd.concat([pd.DataFrame([{"company_id": "","name_full": "(prázdné)"}]), pd_companies])
                pd_companies = pd_companies.where(pd_companies["active"] == 1).dropna(how="all")
                if company_id is None:
                    company_id = ""
                pd_companies['_pick'] = np.where(pd_companies['company_id'] == company_id, True, False)

                partner_vyber(pd_companies)
            st.text_input("Místo:", key=f"issue_head_{issue_id}_place", disabled=(is_new==0))
        with col3:
            st.date_input("Datum vydání:", key=f"issue_head_{issue_id}_date_of_issue", disabled=(is_new==0))
            st.number_input("Celková částka:", key=f"issue_head_{issue_id}_issue_price", disabled=True)
        if f"issue_details_{issue_id}" not in st.session_state:
            if is_new:
                data_detail = []
            else:
                data_detail = issue_head["data"]["issueDetail"]
            st.session_state[f"issue_details_{issue_id}"] = pd.DataFrame(columns=columns_issue_detail, data=data_detail)
        detail_data_editor = st.data_editor(
            data=st.session_state[f"issue_details_{issue_id}"],
            hide_index=True,
                column_config={
                    "issue_id": st.column_config.TextColumn("Issue ID", width="small", disabled=True),
                    "note": st.column_config.TextColumn("Poznámka", width="small", disabled=not is_new),
                    "item_id": st.column_config.TextColumn("Item ID", width="small", disabled=True),
                    "amoung": st.column_config.NumberColumn("Počet", width="small", disabled=not is_new), 
                    "price_peice": st.column_config.NumberColumn("Cena za kus", width="small", disabled=True),
                    "price_row": st.column_config.NumberColumn("Cena za řádku", width="small", disabled=True),
                    "item_name": st.column_config.SelectboxColumn("Předmět", options=list(items_filtered), disabled=not is_new)
                },
                column_order=["item_name", "note", "amoung", "price_peice", "price_row", "item_id"],
                width="stretch",
                key="issue_details_editor",
                num_rows="dynamic"
            )
        if st.button("Přidat", disabled=not is_new):
            details_df = detail_data_editor.copy()
            new_row = [{ "issue_id": issue_id,
                    "note": "",
                        "item_id": None,
                        "amoung": 0,
                        "price_peice": 0,
                        "price_row": 0,
                        "item_name": ""
                        }]
            st.session_state[f"issue_details_{issue_id}"] = pd.concat([details_df, pd.DataFrame(new_row)], ignore_index=True)
            st.rerun()
        issue_head_edited = deepcopy(st.session_state[f"issue_head_orig_{issue_id}"])
        for column_issue_head in columns_issue_head:
            issue_head_edited[column_issue_head] = st.session_state[f"issue_head_{issue_id}_{column_issue_head}"]
        if st.button("Přepočet dokladu"):
            details_df = detail_data_editor.copy()
            details = details_df.to_dict()
            for index, item_name in details["item_name"].items():
                if item_name:
                    details["item_id"][index] = None
                    for item in items:
                        if item["name"] == item_name:
                            details["item_id"][index] = item["item_id"]
                            details["price_peice"][index] = item["price_selling"]
                            if not details["amoung"][index]:
                                details["amoung"][index] = 1
                            details["price_row"][index] = item["price_selling"] * details["amoung"][index]
                else:
                    details["item_id"][index] = None
            st.session_state[f"issue_details_{issue_id}"] = pd.DataFrame(details)
            st.rerun()
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
                #try:
                    #database.from_("issue_head").insert(insert_data).execute()
                details_df = detail_data_editor.copy()
                rows = []
                for row_index in range(len(details_df["issue_id"])):
                    row = {}
                    for column in detail_data_editor:
                        row[column] = details_df[column][row_index]
                        if column in ("amoung", "price_peice", "price_row") and row[column]:
                            row[column] = float(row[column])
                    row["issue_id"] = issue_id
                    row["issue_detail_id"] = str(uuid.uuid4())
                    rows.append(row)
                insert_data["issueDetail"] = rows
                url = f"{fast_api_url_base}{fast_api_url_issue_c}"
                body = download_post_url(url, json.dumps(insert_data), [f"Authorization: Bearer {access_token_new}", "Content-Type: application/json"])
                st.write(f"{body=}")
                body = body.decode('UTF-8')
                issue_insert = json.loads(body)
                body = call_create_issue_from_pre(access_token_new, issue_insert["pre_id"])

                st.session_state.pop(f"issue_head_orig_{issue_id}")
                st.query_params.pop("new", None)
                st.success("Vytvořeno")
                st.toast("Výdejka byla vytvořena", icon="✅")
                #st.switch_page("pages/store/assortment/assortments.py")
            #except Exception as E:
            #    st.error("Nepovedlo se vytvořit výdejku")
            #    st.error(E)
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

if __name__ == "__main__":
    main()