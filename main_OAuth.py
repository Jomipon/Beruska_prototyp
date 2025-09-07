import os
from urllib.parse import urlencode
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# --- načtení .env ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")

# --- vytvoření klienta s ANON klíčem (důležité pro RLS) ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(page_title="Streamlit + Supabase + RLS", page_icon="🔐")
st.title("🔐 Streamlit + Supabase Auth (Google) + RLS")

# --- helper: je uživatel přihlášený? ---
def get_session():
    # V supabase-py v2 se session drží uvnitř auth; můžeme volat:
    try:
        sess = supabase.auth.get_session()
        return sess
    except Exception:
        return None

def ensure_session_state():
    if "sb_session" not in st.session_state:
        st.session_state["sb_session"] = get_session()

ensure_session_state()

# --- přihlášení přes Google ---
def login_with_google():
    # Vytvoříme OAuth URL. Supabase vrací objekt s vlastností .url
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": APP_BASE_URL
        }
    })
    auth_url = getattr(res, "url", None) or res.get("url")
    if not auth_url:
        st.error("Nepodařilo se získat OAuth URL.")
        return
    st.session_state["auth_url"] = auth_url
    st.write("Pokud nedošlo k přesměrování, klikni na odkaz:")
    st.link_button("Pokračovat na Google", auth_url)

# --- zpracování návratu z OAuth: ?code=... ---
def handle_oauth_callback():
    # Streamlit 1.33+: st.query_params je dict[str, list[str]] nebo dict-like
    qp = st.query_params
    code = None
    if isinstance(qp, dict):
        val = qp.get("code")
        if isinstance(val, list):
            code = val[0] if val else None
        elif isinstance(val, str):
            code = val
    if not code:
        return

    try:
        session = supabase.auth.exchange_code_for_session({"auth_code": code})
        # Uložíme session do session_state
        st.session_state["sb_session"] = session
        st.success(f"Přihlášen: {session.user.email}")
        # vyčistit query parametry (abychom neexchangovali znovu při refreshi)
        st.query_params.clear()
    except Exception as e:
        st.error(f"Chyba při výměně kódu za session: {e}")

# --- odhlášení ---
def logout():
    try:
        supabase.auth.sign_out()
    finally:
        st.session_state.pop("sb_session", None)
        st.rerun()

# --- UI sekce: přihlášení/odhlášení ---
handle_oauth_callback()
session = st.session_state.get("sb_session")

auth_col1, auth_col2 = st.columns(2)
with auth_col1:
    if not session or not getattr(session, "user", None):
        st.caption("Nejsi přihlášen.")
        if st.button("Přihlásit se přes Google"):
            login_with_google()
    else:
        st.success(f"Přihlášen jako: {session.user.email}")
with auth_col2:
    if session and getattr(session, "user", None):
        st.button("Odhlásit", on_click=logout)

st.divider()

# --- Databázová část chráněná RLS ---
st.subheader("📦 Moje položky (chráněné RLS)")

if not session or not getattr(session, "user", None):
    st.info("Přihlas se, aby ses dostal k vlastním datům.")
    st.stop()

# Vložení nové položky
with st.form("add_item", clear_on_submit=True):
    content = st.text_input("Nový obsah")
    submitted = st.form_submit_button("Přidat")
    if submitted and content.strip():
        ins = supabase.from_("items").insert({"content": content.strip()}).execute()
        if ins.error:
            st.error(f"Insert error: {ins.error}")
        else:
            st.success("Přidáno.")
            st.rerun()

# Výpis jen mých řádků (RLS)
res = supabase.from_("items").select("*").order("created_at", desc=True).execute()
if res.error:
    st.error(f"Select error: {res.error}")
else:
    rows = res.data or []
    if not rows:
        st.write("Zatím žádné záznamy.")
    else:
        for r in rows:
            st.markdown(f"- **{r.get('content')}**  \n  _{r.get('created_at')}_")

# Volitelně: jednoduché mazání vlastních záznamů
st.subheader("🗑️ Smazat záznam")
to_delete = st.text_input("Zadej ID položky ke smazání (uuid)")
if st.button("Smazat"):
    if to_delete:
        delres = supabase.from_("items").delete().eq("id", to_delete).execute()
        if delres.error:
            st.error(f"Delete error: {delres.error}")
        else:
            st.success("Smazáno, pokud záznam patřil tobě.")
            st.rerun()
