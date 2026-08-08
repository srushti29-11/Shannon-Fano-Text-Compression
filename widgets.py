"""Reusable themed widget factories.

Everything here takes an explicit parent and returns a widget; nothing knows
about the application's state.
"""

import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import (
    BORDER, CARD, CARD_ALT, EMPTY_CHART_MESSAGE, FIELD, FONTS, INK, MUTED,
    NEUTRAL, NEUTRAL_HOVER, PAGE, PLACEHOLDER, SELECTION,
)

# Widgets that scroll their own contents and must keep the wheel for themselves.
SELF_SCROLLING = ("Text", "Treeview")


def create_scrollable_area(parent):
    """A vertically scrollable region. Returns (canvas, inner_frame)."""
    outer = tk.Frame(parent, bg=PAGE)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, bg=PAGE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(canvas, bg=PAGE)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    inner.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfig(window_id, width=event.width),
    )

    return canvas, inner


def bind_mousewheel(root, canvas):
    """Scroll `canvas` with the wheel anywhere except over self-scrolling widgets.

    bind_all is needed because the canvas is almost entirely covered by child
    widgets; without it only the bare background would respond.
    """

    def on_wheel(event):
        widget = event.widget
        while isinstance(widget, tk.Misc) and widget is not canvas:
            if widget.winfo_class() in SELF_SCROLLING:
                return
            widget = widget.master

        if event.num == 4:                       # X11 wheel up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:                     # X11 wheel down
            canvas.yview_scroll(1, "units")
        else:
            # macOS reports small deltas, Windows multiples of 120.
            step = event.delta
            step = int(step / 120) if abs(step) >= 120 else step
            canvas.yview_scroll(-step, "units")

    for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        root.bind_all(sequence, on_wheel)


def create_section(parent, title, pad=15, fill="x"):
    section = tk.LabelFrame(
        parent, text=title, font=FONTS["section"],
        bg=CARD, fg=INK, padx=pad, pady=pad,
    )
    section.pack(fill=fill, padx=20, pady=10)
    return section


def create_card(parent, title):
    """A metric tile. Returns the label holding the value."""
    frame = tk.Frame(parent, bg=CARD_ALT, padx=15, pady=12, relief="solid", bd=1)
    frame.pack(side="left", fill="both", expand=True, padx=5)

    tk.Label(
        frame, text=title, font=FONTS["card_title"], bg=CARD_ALT, fg=MUTED,
    ).pack()

    value = tk.Label(
        frame, text=PLACEHOLDER, font=FONTS["card_value"], bg=CARD_ALT, fg=INK,
    )
    value.pack(pady=(5, 0))
    return value


def create_button(parent, text, command, color, hover_color, compact=False):
    """A coloured button built from a Frame and Label.

    macOS draws tk.Button natively and ignores its bg, so the native button
    flips shade with the OS appearance and no single fg stays readable in both.
    Composing one lets us pin both colours.

    Returns the outer Frame; its only child is the Label, which callers use to
    flash confirmation text.
    """
    button = tk.Frame(parent, bg=color, cursor="hand2")

    label = tk.Label(
        button,
        text=text,
        font=FONTS["button_compact"] if compact else FONTS["button"],
        bg=color,
        fg="white",
        padx=10 if compact else 22,
        pady=4 if compact else 11,
        cursor="hand2",
    )
    label.pack()

    def on_enter(event):
        button.configure(bg=hover_color)
        label.configure(bg=hover_color)

    def on_leave(event):
        button.configure(bg=color)
        label.configure(bg=color)

    for widget in (button, label):
        widget.bind("<Button-1>", lambda event: command())
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    return button


def create_field(parent, height, font):
    """A text area with every colour pinned, including the caret."""
    field = tk.Text(
        parent, height=height, wrap="word", font=font,
        bg=FIELD, fg=INK, insertbackground=INK,
        selectbackground=SELECTION, selectforeground=INK,
        relief="solid", bd=1, highlightthickness=0,
    )
    field.pack(fill="x")
    return field


def create_copy_toolbar(section, command):
    """A right-aligned COPY button packed above the pane it copies.

    `command` is called with the button's Label so it can flash confirmation.
    """
    toolbar = tk.Frame(section, bg=CARD)
    toolbar.pack(fill="x", pady=(0, 6))

    holder = {}
    button = create_button(
        toolbar, "COPY", lambda: command(holder["label"]),
        NEUTRAL, NEUTRAL_HOVER, compact=True,
    )
    button.pack(side="right")
    holder["label"] = button.winfo_children()[0]
    return button


def set_readonly_text(widget, content=""):
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, content)
    widget.config(state="disabled")


def create_chart(parent, figsize):
    figure = Figure(figsize=figsize, dpi=90, facecolor=CARD)
    axis = figure.add_subplot(111)

    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return figure, axis, canvas


def style_axis(axis):
    """Re-pin colours after clear(), which resets them to matplotlib defaults."""
    axis.set_facecolor(CARD)
    axis.tick_params(colors=MUTED)

    for spine in axis.spines.values():
        # clear() does NOT restore visibility, so a chart drawn after the empty
        # state would otherwise come back with no axis lines at all.
        spine.set_visible(True)
        spine.set_color(BORDER)


def reset_axis(axis, title, ylabel, xlabel=None):
    axis.clear()
    axis.set_title(title, color=INK)
    if xlabel:
        axis.set_xlabel(xlabel, color=INK)
    axis.set_ylabel(ylabel, color=INK)
    style_axis(axis)


def show_empty_chart(axis, canvas, message=EMPTY_CHART_MESSAGE):
    """Say why a chart is blank instead of showing bare axes."""
    axis.clear()
    axis.set_facecolor(CARD)
    axis.set_xticks([])
    axis.set_yticks([])

    for spine in axis.spines.values():
        spine.set_visible(False)

    axis.text(
        0.5, 0.5, message, ha="center", va="center",
        color=MUTED, fontsize=11, transform=axis.transAxes,
    )

    # Deferred: Tk redraws on the first <Configure> anyway, so a synchronous
    # draw would only block on a figure nobody is looking at yet.
    canvas.draw_idle()
