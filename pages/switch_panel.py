import streamlit as st

def main_menu():
    menu = st.expander("Menu")
    with menu:
        tab_base, tab_company, tab_assortment, tab_settings, tab_test = st.tabs(["Přehled", "Partneři", "Sklad", "Nastavení", "Test"])
        with tab_base:
            st.page_link("pages/board.py", label="Přehled")
        with tab_company:
            st.page_link("pages/company/companies.py", label="Seznam Partnerů")
        with tab_assortment:
            st.page_link("pages/assortment/assortments.py", label="Seznam sortimentu")
        with tab_settings:
            st.page_link("pages/settings/settings.py", label="Nastavení")
        with tab_test:
            st.page_link("pages/page_test.py", label="Test")

