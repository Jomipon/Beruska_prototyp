import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")

st.set_page_config(page_title="Streamlit + Supabase + RLS", page_icon="🔐")
st.title("🔐 Streamlit + Supabase Auth (Google) + RLS")

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def logout():
    try:
        supabase.auth.sign_out()
    finally:
        st.session_state.pop("sb_session", None)
        st.session_state.pop("sb_tokens", None)

supabase = get_client()

# 1) Po načtení stránky zpracuj ?code=... JEN JEDNOU
code = st.query_params.get("code")
if code and "sb_tokens" not in st.session_state:
    try:
        sess = supabase.auth.exchange_code_for_session({"auth_code": code})
        # ulož tokeny do session_state pro další render
        st.session_state["sb_tokens"] = (
            sess.session.access_token,
            sess.session.refresh_token,
        )
        # smaž ?code=... z URL a rerun
        st.query_params.clear()
    except Exception as e:
        st.error(f"OAuth výměna selhala: {e}")
    st.rerun()

# 2) Při každém renderu „rehydratuj“ klienta ze session_state
if "sb_tokens" in st.session_state:
    at, rt = st.session_state["sb_tokens"]
    supabase.auth.set_session(at, rt)

# 3) Teprve teď zjišťuj, zda je uživatel přihlášen
sess = supabase.auth.get_session()
if sess and getattr(sess, "user", None):
    st.success(f"Přihlášen: {sess.user.email}")
    st.button("Odhlásit", on_click=logout)
else:
    st.info("Nejsi přihlášen.")
    # Vygeneruj OAuth URL…
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": APP_BASE_URL}
    })
    auth_url = getattr(res, "url", None) or res.get("url")
    # …a raději odkaz otevři VE STEJNÉM TABU (ne novém):
    st.markdown(f'<a href="{auth_url}" class="st-emotion-cache-7ym5gk ea3mdgi1">Pokračovat na Google</a>',
                unsafe_allow_html=True)
    # (nebo prostě st.markdown(f"[Pokračovat na Google]({auth_url})", unsafe_allow_html=True))

def get_data_items():
    items = supabase.from_("items").select("*").order("created_at").execute()
    return items
def show_data_items(data):
    df = pd.DataFrame(data)
    df = df.assign(_selected=False)
    #df = df.assign(url=f"https://jomipon-beruska-prototyp.streamlit.app/?item={df.id}")
    #df = df.assign(url=f"https://localhost:8501//?item={df.id}")
    df = df.assign(url=df.id)
    #df["url"] = df["url"].apply(lambda x: f"https://jomipon-beruska-prototyp.streamlit.app/?item={x}")
    df["url"] = df["url"].apply(lambda x: f"{APP_BASE_URL}?item={x}")
    df = df[["_selected", "content", "url", "id", "owner_id", "created_at"]]
    df_view = st.data_editor(data=df.assign(_selected=False),
                    hide_index=True,
                    disabled=["id", "owner_id", "content", "created_at"],
                    column_config={"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
                                    "id": st.column_config.Column("id"),
                                    "url": st.column_config.LinkColumn("", display_text="Detail")},
                    column_order=["_selected", "content", "url"],
                    use_container_width=True)
    return df_view
if sess and getattr(sess, "user", None):
    items = st.query_params.get("items")
    item = st.query_params.get("item")
    if items:
        pass
    if item:
        if items:
            st.write(f"{items=}")
        if item:
            st.link_button("Home page", url=APP_BASE_URL)
            st.write(f"{item=}")
            item = supabase.from_("items").select("*").filter("id", "eq", item).execute()
            initial = item.data[0]["content"] if item and item.data else ""
            if "content" not in st.session_state:
                st.session_state["content"] = initial
            with st.form("edit_item"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Content:", key="content")
                with col2:
                    st.text_input("id", item.data[0]["id"],disabled=True)
                    st.text_input("owner id", item.data[0]["owner_id"],disabled=True)
                with col3:
                    st.text_input("created at", item.data[0]["created_at"],disabled=True)
                if st.form_submit_button("Uložit"):
                    try:
                        new_content = st.session_state["content"]
                        upd = supabase.from_("items").update({"content": new_content}).eq("id", item.data[0]["id"]).execute()
                        #item.data[0]["content"] = text_content
                        st.success(f"Uloženo {new_content}.")
                    except Exception as e:
                        st.error(f"Update error: {e}")
            
    else:
        # --- Databázová část chráněná RLS ---
        st.subheader("📦 Moje položky (chráněné RLS)")
        # Vložení nové položky
        with st.form("add_item", clear_on_submit=True):
            content = st.text_input("Nový obsah")
            submitted = st.form_submit_button("Přidat")
            if submitted and content.strip():
                try:
                    ins = supabase.from_("items").insert({"content": content.strip()}).execute()
                    itemName = ins.data[0]["content"]
                    st.success(f"Přidáno {itemName}.")
                except Exception as e:
                    st.error(f"Insert error: {e}")
            else:
                st.write(f"Nepovedlo se přidat položku {content.strip()}")
        #items = supabase.from_("items").select("*").order("created_at").execute()
        items = get_data_items()
        if items.data:
            df_view = show_data_items(items.data)
            selected = df_view[df_view["_selected"]]
            if st.button("Smazat označené záznamy", disabled=selected.empty):
                for row in selected.iterrows():
                    supabase.from_("items").delete().match({"id": row[1]["id"]}).execute()
                st.rerun()
            if st.button("Označená data"):
                if selected.empty:
                    st.warning("Nic není označeno")
                else:
                    st.write("Označené řádky:")
                    st.dataframe(selected)

                    # příklad: vezmu první označený řádek a přečtu hodnoty
                    #first = selected.iloc[0]
                    #st.success(f"První označený: id={first['id']}, jméno={first['name']}, score={first['score']}")
        else:
            st.write("Žádná data")
        #for row in items.data:
        #    st.write(f"{row['content']} - {row['owner_id']}")



                
            
