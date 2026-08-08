"""Shannon-Fano text compression - graphical front end.

The algorithm and all statistics live in shannon_fano_core; this module only
builds widgets and paints results into them.
"""

import tkinter as tk
from tkinter import ttk

import theme
from shannon_fano_core import analyze, display_character, group_bits
from widgets import (
    bind_mousewheel, create_button, create_card, create_chart,
    create_copy_toolbar, create_field, create_scrollable_area, create_section,
    reset_axis, set_readonly_text, show_empty_chart,
)

FREQUENCY_TITLE = "Character Frequency Distribution"
COMPARISON_TITLE = "Original vs Compressed Data Size"

# key, card heading, how to format the value. Adding a metric means one line
# here and nothing else.
METRIC_SPECS = (
    ("original", "ORIGINAL SIZE", lambda r: f"{r.original_size} bits"),
    ("compressed", "COMPRESSED SIZE", lambda r: f"{r.compressed_size} bits"),
    ("saved", "SPACE SAVED", lambda r: f"{r.space_saved:.2f}%"),
    ("efficiency", "CODING EFFICIENCY", lambda r: f"{r.efficiency:.2f}%"),
    ("entropy", "ENTROPY", lambda r: f"{r.entropy:.3f} bits"),
    ("avg_length", "AVERAGE CODE LENGTH", lambda r: f"{r.average_length:.3f} bits"),
    ("unique", "UNIQUE CHARACTERS", lambda r: str(len(r.frequency))),
)

# name, heading, pixel width
COLUMN_SPECS = (
    ("character", "Character", 130),
    ("frequency", "Frequency", 120),
    ("probability", "Probability", 140),
    ("code", "Shannon-Fano Code", 200),
    ("length", "Code Length", 120),
)


class ShannonFanoApp:
    """The full analysis window."""

    def __init__(self, root):
        self.root = root
        root.title("Shannon-Fano Text Compression")
        root.geometry("1100x800")
        # The content needs 964px and there is no horizontal scrollbar, so a
        # narrower window would clip the cards and table rather than reflow.
        root.minsize(1000, 600)
        root.configure(bg=theme.PAGE)

        theme.apply_ttk_theme(root)

        self.canvas, self.body = create_scrollable_area(root)
        bind_mousewheel(root, self.canvas)

        self.cards = {}
        self.sort_state = {"column": None, "descending": False}
        # The encoded pane shows a byte-grouped string, so copying reads from
        # here rather than from the widget.
        self.raw = {"encoded": "", "decoded": ""}

        self._build_header()
        self._build_input()
        self._build_cards()
        self._build_table()
        self._build_panes()
        self._build_charts()
        self._build_footer()
        self._build_buttons()
        self._bind_keys()

        self.show_empty_charts()
        self.input.focus_set()

    # ---------- construction ----------

    def _build_header(self):
        header = tk.Frame(self.body, bg=theme.HEADER_BG, padx=25, pady=22)
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header, text="SHANNON-FANO TEXT COMPRESSION",
            font=theme.FONTS["title"], bg=theme.HEADER_BG, fg=theme.HEADER_FG,
        ).pack()
        tk.Label(
            header, text="Lossless Text Compression & Analysis Tool",
            font=theme.FONTS["subtitle"], bg=theme.HEADER_BG, fg=theme.HEADER_SUB,
        ).pack(pady=(6, 0))

    def _build_input(self):
        section = create_section(self.body, "  INPUT TEXT  ")

        self.input = create_field(section, height=6, font=theme.FONTS["input"])
        self.input.bind("<<Modified>>", self._on_input_modified)

        self.char_count = tk.Label(
            section, text="0 characters", font=theme.FONTS["small"],
            bg=theme.CARD, fg=theme.MUTED, anchor="w",
        )
        self.char_count.pack(fill="x", pady=(4, 0))

        self.button_bar = tk.Frame(section, bg=theme.CARD)
        self.button_bar.pack(pady=(12, 6))

        self.status = tk.Label(
            section, text="", font=theme.FONTS["status"],
            bg=theme.CARD, fg=theme.MUTED,
        )
        self.status.pack(fill="x")

    def _build_cards(self):
        section = create_section(self.body, "  COMPRESSION ANALYSIS  ")

        for specs, pady in ((METRIC_SPECS[:4], 0), (METRIC_SPECS[4:], (10, 0))):
            row = tk.Frame(section, bg=theme.CARD)
            row.pack(fill="x", pady=pady)
            for key, heading, _ in specs:
                self.cards[key] = create_card(row, heading)

    def _build_table(self):
        section = create_section(self.body, "  SHANNON-FANO CODES  ")

        frame = tk.Frame(section, bg=theme.CARD)
        frame.pack(fill="both", expand=True)

        self.table = ttk.Treeview(
            frame,
            columns=tuple(name for name, _, _ in COLUMN_SPECS),
            show="headings",
            height=10,
        )
        for name, heading, width in COLUMN_SPECS:
            self.table.heading(
                name, text=heading,
                command=lambda column=name: self._sort_by(column),
            )
            self.table.column(name, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_panes(self):
        encoded = create_section(self.body, "  ENCODED / COMPRESSED DATA  ")
        create_copy_toolbar(encoded, lambda label: self._copy("encoded", label))
        self.encoded = create_field(encoded, height=7, font=theme.FONTS["mono"])
        self.encoded.config(state="disabled")

        decoded = create_section(self.body, "  DECODED TEXT  ")
        create_copy_toolbar(decoded, lambda label: self._copy("decoded", label))
        self.decoded = create_field(decoded, height=5, font=theme.FONTS["body"])
        self.decoded.config(state="disabled")

    def _build_charts(self):
        frequency = create_section(
            self.body, "  CHARACTER FREQUENCY DISTRIBUTION  ", pad=10, fill="both",
        )
        self.freq_figure, self.freq_axis, self.freq_canvas = create_chart(
            frequency, (10, 4.8),
        )

        comparison = create_section(
            self.body, "  ORIGINAL VS COMPRESSED SIZE  ", pad=10, fill="both",
        )
        self.comp_figure, self.comp_axis, self.comp_canvas = create_chart(
            comparison, (10, 4.5),
        )

    def _build_footer(self):
        tk.Label(
            self.body, text="Shannon-Fano Coding • Lossless Text Compression",
            font=theme.FONTS["small"], bg=theme.PAGE, fg=theme.MUTED, pady=15,
        ).pack()

    def _build_buttons(self):
        create_button(
            self.button_bar, "COMPRESS & ANALYZE", self.analyze,
            theme.ACCENT, theme.ACCENT_HOVER,
        ).pack(side="left", padx=8)

        create_button(
            self.button_bar, "CLEAR", self.clear,
            theme.NEUTRAL, theme.NEUTRAL_HOVER,
        ).pack(side="left", padx=8)

    def _bind_keys(self):
        def analyze_shortcut(event=None):
            self.analyze()
            # "break" stops the remaining bindtags, which is what keeps the
            # Text widget's own Return binding from also inserting a newline.
            # It must be bound on the widget: the class binding runs first.
            return "break"

        def clear_shortcut(event=None):
            self.clear()
            return "break"

        # Plain Return still inserts a newline; only the chords are taken.
        for sequence in ("<Command-Return>", "<Control-Return>"):
            self.input.bind(sequence, analyze_shortcut)
            self.root.bind(sequence, analyze_shortcut)

        self.input.bind("<Escape>", clear_shortcut)
        self.root.bind("<Escape>", clear_shortcut)

    # ---------- handlers ----------

    def analyze(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")

        if not text:
            self.set_status("⚠  Enter some text first.", theme.WARNING)
            return

        result = analyze(text)
        self.render(result)

        if result.is_lossless:
            self.set_status(
                f"✓  Lossless — decoded output matches the original  "
                f"({result.original_size} → {result.compressed_size} bits, "
                f"{result.space_saved:.1f}% saved)",
                theme.SUCCESS,
            )
        else:
            self.set_status(
                "✗  Decoded output does not match the original.", theme.DANGER,
            )

    def clear(self):
        self.input.delete("1.0", tk.END)
        self.update_char_count()
        self.set_status("")

        self.raw = {"encoded": "", "decoded": ""}
        set_readonly_text(self.encoded)
        set_readonly_text(self.decoded)

        self.table.delete(*self.table.get_children())
        self.sort_state["column"] = None
        self._refresh_headings()

        for card in self.cards.values():
            card.config(text=theme.PLACEHOLDER)

        self.show_empty_charts()

    def render(self, result):
        for key, _, fmt in METRIC_SPECS:
            self.cards[key].config(text=fmt(result))

        self.table.delete(*self.table.get_children())
        for character, freq in result.symbols:
            self.table.insert("", "end", values=(
                display_character(character),
                freq,
                f"{result.probabilities[character]:.4f}",
                result.codes[character],
                len(result.codes[character]),
            ))

        # Rows are inserted in the algorithm's order, so any sort is stale.
        self.sort_state["column"] = None
        self._refresh_headings()

        self.raw = {"encoded": result.encoded, "decoded": result.decoded}
        # Grouped for reading; clipboard and bit counts use the raw string.
        set_readonly_text(self.encoded, group_bits(result.encoded))
        set_readonly_text(self.decoded, result.decoded)

        self.draw_frequency_chart(result.frequency)
        self.draw_comparison_chart(result.original_size, result.compressed_size)

    def set_status(self, message, color=theme.MUTED):
        self.status.config(text=message, fg=color)

    def update_char_count(self):
        text = self.input.get("1.0", "end-1c")
        self.char_count.config(
            text=f"{len(text)} characters · {len(set(text))} unique"
            if text else "0 characters"
        )

    def _on_input_modified(self, event):
        # Tk fires <<Modified>> whenever the flag changes, including when we
        # reset it below -- the guard stops that second firing from recursing.
        if not self.input.edit_modified():
            return
        self.update_char_count()
        self.input.edit_modified(False)

    def _copy(self, key, label):
        value = self.raw[key]
        if not value:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(value)

        # A clipboard write is otherwise invisible, so say so briefly.
        label.configure(text="COPIED")
        self.root.after(1200, lambda: label.configure(text="COPY"))

    # ---------- table sorting ----------

    @staticmethod
    def _sort_key(value):
        """Numeric where possible -- frequency and length must not sort as text."""
        try:
            return (0, float(value), "")
        except ValueError:
            return (1, 0.0, value)

    def _refresh_headings(self):
        for name, heading, _ in COLUMN_SPECS:
            arrow = ""
            if self.sort_state["column"] == name:
                arrow = "  ▼" if self.sort_state["descending"] else "  ▲"
            self.table.heading(name, text=heading + arrow)

    def _sort_by(self, column):
        descending = (
            not self.sort_state["descending"]
            if self.sort_state["column"] == column
            else False
        )

        # .set() preserves strings; .item()["values"] coerces "0010" to 10.
        rows = [
            (self.table.set(item, column), item)
            for item in self.table.get_children("")
        ]
        rows.sort(key=lambda row: self._sort_key(row[0]), reverse=descending)

        for index, (_, item) in enumerate(rows):
            self.table.move(item, "", index)

        self.sort_state.update(column=column, descending=descending)
        self._refresh_headings()

    # ---------- charts ----------

    def show_empty_charts(self):
        show_empty_chart(self.freq_axis, self.freq_canvas)
        show_empty_chart(self.comp_axis, self.comp_canvas)

    def draw_frequency_chart(self, frequency):
        reset_axis(self.freq_axis, FREQUENCY_TITLE, "Frequency", "Characters")

        labels = [display_character(character) for character in frequency]
        bars = self.freq_axis.bar(labels, list(frequency.values()),
                                  color=theme.ACCENT)

        self.freq_axis.tick_params(axis="x", rotation=45)
        self.freq_axis.bar_label(bars, padding=3, fontsize=9, color=theme.INK)

        self.freq_figure.tight_layout()
        self.freq_canvas.draw()

    def draw_comparison_chart(self, original_size, compressed_size):
        reset_axis(self.comp_axis, COMPARISON_TITLE, "Size (bits)")

        bars = self.comp_axis.bar(
            ["Original", "Compressed"], [original_size, compressed_size],
            color=[theme.NEUTRAL, theme.ACCENT],
        )
        self.comp_axis.bar_label(
            bars, fmt="%d bits", padding=3, fontweight="bold", color=theme.INK,
        )

        self.comp_figure.tight_layout()
        self.comp_canvas.draw()


def main():
    root = tk.Tk()
    ShannonFanoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
