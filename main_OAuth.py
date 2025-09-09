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
        st.rerun()
    except Exception as e:
        st.error(f"OAuth výměna selhala: {e}")

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
if sess and getattr(sess, "user", None):
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
    items = supabase.from_("items").select("*").order("created_at").execute()
    if items.data:
        df = pd.DataFrame(items.data)
        #st.dataframe(data=df[["content","id"]], use_container_width=True,hide_index=True,selection_mode="single-row")
        st.dataframe(data=df[["content","id"]], use_container_width=True,hide_index=True)
        #st.data_editor(data=df)
    else:
        st.write("Žádná data")
    #for row in items.data:
    #    st.write(f"{row['content']} - {row['owner_id']}")



                
            
