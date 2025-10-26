import streamlit as st

def set_session_from_params(database):
    code = st.query_params.get("code")
    if code and "sb_tokens" not in st.session_state:
        try:
            sess = database.auth.exchange_code_for_session({"auth_code": code})
            # ulož tokeny do session_state pro další render
            st.session_state["sb_tokens"] = (
                sess.session.access_token,
                sess.session.refresh_token,
            )
        except Exception as e:
            st.error(f"OAuth výměna selhala: {e}")
        finally:
            # smaž ?code=... z URL a rerun
            st.query_params.clear()
        st.rerun()
def get_session_from_session_state(session, database, cookies):
    if session is None and "sb_tokens" in st.session_state:
        try:
            at, rt = st.session_state["sb_tokens"]
            if cookies is not None and (cookies["acceess_token"] != at or cookies["refresh_token"] != rt):
                cookies["acceess_token"] = at
                cookies["refresh_token"] = rt
                cookies.save()
            if database.auth.email is None:
                database.auth.set_session(at, rt)
            #session = database.auth.get_session()
        except Exception as e:
            pass
        
    return session
def get_session_from_cookies(session, database, cookies):
    if session is None:
        if (not session or "sb_tokens" not in st.session_state):
            if cookies is not None and cookies.ready():
                if "acceess_token" in cookies:
                    if "refresh_token" in cookies:
                        try:
                            at = cookies["acceess_token"]
                            rt = cookies["refresh_token"]
                            database.auth.set_session(at, rt)
                            st.session_state["sb_tokens"] = (at,rt,)
                        except Exception as e:
                            pass
                        try:
                            session = database.auth.get_session()
                        except:
                            session = None
    return session
def user_create(email, password):
    created_user = st.session_state["sb_database"].auth.sign_up({"email": email, "password": password})
    return created_user
def user_login(username, password):
    user = st.session_state["sb_database"].auth.sign_in_with_password({"email": username, "password": password})
    return user
def register_frame():
    register_email = st.text_input("Email:")
    regiter_password = st.text_input("Heslo:", type="password")
    if st.form_submit_button("Vytvořit uživatele"):
        try:
            created_user = user_create(register_email, regiter_password)
            st.write(created_user)
        except Exception as e:
            st.error("Nepovedlo se vytvořit uživatele")
            #st.error(e)
        
def login_frame(cookies, app_url_base):
    input_username = st.text_input("Email:")
    input_password = st.text_input("Heslo:", type="password")
    if st.form_submit_button("Přihlásit"):
        try:
            user = user_login(input_username, input_password)
        except Exception as e:
            user = None
        if user:
            session = st.session_state["sb_database"].auth.get_session()
            at = session.access_token
            rt = session.refresh_token
            st.session_state["sb_tokens"] = (
                session.access_token,
                session.refresh_token,
            )
            cookies["acceess_token"] = at
            cookies["refresh_token"] = rt
            cookies.save()
            st.session_state["zobrazit_prihlaseno"] = True
        else:
            st.error("Jméno nebo heslo je neplatné")
        st.rerun()
    res = st.session_state["sb_database"].auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": app_url_base}
    })
    auth_url = getattr(res, "url", None) or res.get("url")

def get_login_frame(cookies, app_url_base):
    tab_login, tab_register = st.tabs(["Přihlásit", "Registrace"])
    with tab_login:
        with st.form("login", clear_on_submit=True):
            login_frame(cookies, app_url_base)
    with tab_register:
        with st.form("register", clear_on_submit=True):
            register_frame()
def get_loged_frame(session, cookies):
    st.markdown("# L.E.J.S.E.K.")
    st.write(f"Přihlášený uživatel: {session.user.email}")
    if st.button("Odhlásit"):
        try:
            st.session_state["sb_database"].auth.sign_out()
            st.session_state["show_loged_out"] = True
        finally:
            st.session_state.pop("token", None)
            st.session_state.pop("sb_tokens", None)
        try:
            cookies["acceess_token"] = ""
            cookies["refresh_token"] = ""
            cookies.save()
        except:
            pass
        st.rerun()

def login_pageframe_by_gmail(database, app_base_url):
    st.markdown("**Google**")
    res = database.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": app_base_url}
    })
    auth_url = getattr(res, "url", None) or res.get("url")
    # …a raději odkaz otevři VE STEJNÉM TABU (ne novém):
    st.markdown(f'<a href="{auth_url}" target="_self" class="st-emotion-cache-7ym5gk ea3mdgi1">Přihlásit pomocí Google účtu</a>', unsafe_allow_html=True)
    #st.markdown(f"[Přihlásit pomocí Google účtu ]({auth_url})", unsafe_allow_html=True)
    if st.form_submit_button("Skrýt"):
        st.session_state["show_login"] = False
        st.rerun()
