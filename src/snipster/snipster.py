import reflex as rx

from snipster.ui import navbar, snippets


def header():
    return rx.text("Snipster", font_size="2xl", font_weight="bold")


def snippet_box(title: str, code: str):
    return rx.box(
        rx.text(title, font_weight="bold"),
        rx.code_block(code, language="python"),
        border="1px solid #ccc",
        border_radius="8px",
        padding="1em",
        margin_y="1em",
    )


def index():
    return rx.vstack(navbar.navbar(), snippets.snippet_list())


app = rx.App()
app.add_page(index, title="Snipster")
