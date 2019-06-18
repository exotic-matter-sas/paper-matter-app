from ftests.pages.base_page import BasePage


class DocumentViewPage(BasePage):
    url = '/app/#/home?doc={}'

    document_title = '#document-title'
    document_close = '#id="document-title"'

