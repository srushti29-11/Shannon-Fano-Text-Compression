"""Colours, fonts and ttk styling for the graphical app.

Every colour is pinned. Tk falls back to OS colours for any option left unset,
and in macOS dark mode systemTextColor resolves to pure white -- which turns
unset foregrounds invisible against these light backgrounds.
"""

from tkinter import ttk

# Surfaces
PAGE = "#f4f6f8"
CARD = "white"
CARD_ALT = "#eef2f7"
FIELD = "#f8fafc"

# Text and lines
INK = "#111827"
MUTED = "#6b7280"
BORDER = "#d1d5db"

# Actions
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
NEUTRAL = "#6b7280"
NEUTRAL_HOVER = "#4b5563"

# Header band
HEADER_BG = "#1f2937"
HEADER_FG = "white"
HEADER_SUB = "#d1d5db"

# Feedback
SELECTION = "#bfdbfe"
SUCCESS = "#047857"
WARNING = "#b45309"
DANGER = "#b91c1c"

FONTS = {
    "title": ("Arial", 24, "bold"),
    "subtitle": ("Arial", 11),
    "section": ("Arial", 12, "bold"),
    "card_title": ("Arial", 10, "bold"),
    "card_value": ("Arial", 17, "bold"),
    "body": ("Arial", 11),
    "input": ("Arial", 12),
    "small": ("Arial", 9),
    "status": ("Arial", 10, "bold"),
    "button": ("Arial", 11, "bold"),
    "button_compact": ("Arial", 9, "bold"),
    "mono": ("Consolas", 10),
}

PLACEHOLDER = "--"
EMPTY_CHART_MESSAGE = "Run an analysis to see the chart"


def apply_ttk_theme(root):
    """Style the ttk widgets so they stop following the OS appearance.

    The aqua theme accepts these options into the style database but paints
    natively and ignores them; clam actually honours them. Without this the
    table renders as dark native rows inside a white card.
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=CARD,
        fieldbackground=CARD,
        foreground=INK,
        rowheight=24,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=CARD_ALT,
        foreground=INK,
        borderwidth=0,
        font=FONTS["card_title"],
    )
    style.map(
        "Treeview",
        background=[("selected", SELECTION)],
        foreground=[("selected", INK)],
    )
    style.configure(
        "Vertical.TScrollbar",
        background=CARD_ALT,
        troughcolor=PAGE,
        bordercolor=BORDER,
        arrowcolor=MUTED,
    )

    return style
