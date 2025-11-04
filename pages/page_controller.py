import streamlit as st

class Page_controller():
    def __init__(self):
        self._pages = []
        self._navigation = None

    def page_create(self, file_script, title, url_path):
        page = st.Page(file_script,  title=title,  url_path=url_path)
        self._pages.append(page)
        return page

    def create_page_navigator(self):
        self._navigation = st.navigation(self._pages, position="hidden")
    
    def run(self):
        self._navigation.run()