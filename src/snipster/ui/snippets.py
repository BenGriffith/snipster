import reflex as rx
import requests


def snippet_card(snippet: dict) -> rx.Component:
    return rx.box(
        rx.heading(snippet["title"], size="6"),
        rx.text(snippet["description"]),
        rx.code(snippet["code"]),
        border="1px solid #ccc",
        padding="1em",
        border_radius="md",
        width="100%",
    )


def snippet_list() -> rx.Component:
    response = requests.get("http://localhost:8000/snippets/")
    snippets = response.json() if response.ok else []
    return rx.stack(
        *[snippet_card(s) for s in snippets],
        spacing="4",
        padding="2em",
        width="100%",
    )
