"""Tests for the graphical app.

These drive a real Tk instance. They skip cleanly on a machine with no display.

Two conventions matter here and cost real debugging time to learn:

* Use ``root.update()``, never ``update_idletasks()`` -- the latter drains only
  idle tasks and does not deliver virtual events such as ``<<Modified>>``.
* Send keyboard events to the *widget*, not the toplevel. A toplevel routes them
  to its focus widget, and window focus is unreliable when other processes are
  competing for it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def app():
    pytest.importorskip("matplotlib")
    tk = pytest.importorskip("tkinter")

    from app import ShannonFanoApp

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available")

    instance = ShannonFanoApp(root)
    # The window must stay mapped: a withdrawn Tk window has no laid-out size
    # (so the canvas cannot scroll) and cannot take focus (so key events are
    # never delivered). Park it off-screen instead of hiding it.
    root.geometry("1100x800+-3000+-3000")
    root.update()
    try:
        yield instance
    finally:
        root.destroy()


def analyzed(app, text="AABBBCCCC"):
    app.input.delete("1.0", "end")
    app.input.insert("1.0", text)
    app.analyze()
    app.root.update()
    return app


def table_column(app, name):
    # .set() preserves strings; .item()["values"] coerces "0010" to 10.
    return [app.table.set(item, name) for item in app.table.get_children("")]


# ---------------------------------------------------------------- rendering

def test_cards_show_spec_values(app):
    analyzed(app)
    assert app.cards["original"].cget("text") == "72 bits"
    assert app.cards["compressed"].cget("text") == "14 bits"
    assert app.cards["saved"].cget("text") == "80.56%"
    assert app.cards["efficiency"].cget("text") == "98.39%"
    assert app.cards["entropy"].cget("text") == "1.530 bits"
    assert app.cards["avg_length"].cget("text") == "1.556 bits"
    assert app.cards["unique"].cget("text") == "3"


def test_table_matches_spec(app):
    analyzed(app)
    assert table_column(app, "character") == ["C", "B", "A"]
    assert table_column(app, "code") == ["0", "10", "11"]
    assert table_column(app, "length") == ["1", "2", "2"]


def test_special_characters_get_labels(app):
    analyzed(app, "a b\nc\td")
    shown = table_column(app, "character")
    assert "[SPACE]" in shown and "[ENTER]" in shown and "[TAB]" in shown


def test_control_characters_are_escaped_not_blank(app):
    analyzed(app, "a\x00b\x07c")
    shown = table_column(app, "character")
    assert "\\x00" in shown and "\\x07" in shown
    assert all(cell.strip() for cell in shown)


def test_encoded_pane_is_grouped_but_clipboard_source_is_raw(app):
    analyzed(app)
    assert app.encoded.get("1.0", "end-1c") == "11111010 100000"
    assert app.raw["encoded"] == "11111010100000"
    assert app.decoded.get("1.0", "end-1c") == "AABBBCCCC"


def test_readonly_panes_stay_disabled(app):
    analyzed(app)
    assert app.encoded.cget("state") == "disabled"
    assert app.decoded.cget("state") == "disabled"


# ---------------------------------------------------------------- status strip

def test_status_reports_lossless_inline(app):
    import theme
    analyzed(app)
    assert app.status.cget("fg") == theme.SUCCESS
    assert "Lossless" in app.status.cget("text")


def test_empty_input_warns_inline_without_a_dialog(app):
    import theme
    app.input.delete("1.0", "end")
    app.analyze()
    assert app.status.cget("fg") == theme.WARNING
    assert app.status.cget("text").startswith("⚠")
    assert not app.table.get_children()


# ---------------------------------------------------------------- clear

def test_clear_resets_everything(app):
    import theme
    analyzed(app)
    app.clear()
    app.root.update()

    assert {c.cget("text") for c in app.cards.values()} == {theme.PLACEHOLDER}
    assert not app.table.get_children()
    assert app.status.cget("text") == ""
    assert app.input.get("1.0", "end-1c") == ""
    assert app.char_count.cget("text") == "0 characters"
    assert app.raw == {"encoded": "", "decoded": ""}


# ---------------------------------------------------------------- charts

def test_charts_start_in_the_empty_state(app):
    for axis in (app.freq_axis, app.comp_axis):
        assert [t.get_text() for t in axis.texts] == [
            "Run an analysis to see the chart"
        ]
        assert not any(s.get_visible() for s in axis.spines.values())


def test_chart_recovers_axes_after_the_empty_state(app):
    """Regression: axis.clear() does NOT restore spine visibility.

    Without style_axis re-asserting it, every chart after the first analysis
    rendered with no axis lines at all.
    """
    analyzed(app)
    assert all(s.get_visible() for s in app.freq_axis.spines.values())
    assert len(app.freq_axis.get_xticks()) > 0
    assert len(app.freq_axis.get_yticks()) > 0
    assert len(app.freq_axis.patches) == 3


def test_chart_recovers_after_clear_too(app):
    analyzed(app)
    app.clear()
    app.root.update()
    assert not app.freq_axis.patches

    analyzed(app)
    assert len(app.freq_axis.patches) == 3
    assert all(s.get_visible() for s in app.freq_axis.spines.values())


def test_comparison_chart_labels_bits(app):
    analyzed(app)
    labels = [t.get_text() for t in app.comp_axis.texts]
    assert labels == ["72 bits", "14 bits"]


# ---------------------------------------------------------------- scrolling

def test_wheel_scrolls_the_page(app):
    app.canvas.yview_moveto(0)
    app.root.update()
    before = app.canvas.yview()[0]

    for _ in range(5):
        app.canvas.event_generate("<MouseWheel>", delta=-3)
    app.root.update()

    assert app.canvas.yview()[0] > before


@pytest.mark.parametrize("widget_name", ["encoded", "table"])
def test_wheel_over_self_scrolling_widgets_leaves_the_page(app, widget_name):
    app.canvas.yview_moveto(0.5)
    app.root.update()
    held = app.canvas.yview()[0]

    widget = getattr(app, widget_name)
    for _ in range(5):
        widget.event_generate("<MouseWheel>", delta=-3)
    app.root.update()

    assert app.canvas.yview()[0] == pytest.approx(held)


def test_minsize_covers_required_width(app):
    app.root.update()
    assert app.root.minsize()[0] >= app.body.winfo_reqwidth()


# ---------------------------------------------------------------- keyboard

def test_ctrl_return_analyzes(app):
    app.input.delete("1.0", "end")
    app.input.insert("1.0", "AABBBCCCC")
    app.input.focus_force()
    app.input.event_generate("<Control-Return>")
    app.root.update()
    assert app.cards["original"].cget("text") == "72 bits"


def test_ctrl_return_does_not_also_insert_a_newline(app):
    """Regression: the Text class binding for Return runs before the toplevel's,
    so the shortcut used to analyze AND type a newline into the box."""
    app.input.delete("1.0", "end")
    app.input.insert("1.0", "AABBBCCCC")
    app.input.focus_force()
    app.input.event_generate("<Control-Return>")
    app.root.update()
    assert app.input.get("1.0", "end-1c") == "AABBBCCCC"
    # Also assert the shortcut fired, so this cannot pass by nothing happening.
    assert app.cards["original"].cget("text") == "72 bits"


def test_escape_clears(app):
    import theme
    analyzed(app)
    app.input.focus_force()
    app.input.event_generate("<Escape>")
    app.root.update()
    assert {c.cget("text") for c in app.cards.values()} == {theme.PLACEHOLDER}
    assert not app.table.get_children()


def test_plain_return_still_inserts_a_newline(app):
    app.input.delete("1.0", "end")
    app.input.insert("1.0", "AB")
    app.input.focus_force()
    app.input.event_generate("<Return>")
    app.root.update()
    assert "\n" in app.input.get("1.0", "end-1c")


# ---------------------------------------------------------------- char count

def test_char_count_tracks_the_input(app):
    app.input.delete("1.0", "end")
    app.input.insert("1.0", "AABBBCCCC")
    app.root.update()
    assert app.char_count.cget("text") == "9 characters · 3 unique"


def test_char_count_does_not_recurse(app):
    """The <<Modified>> handler resets the flag, which re-fires the event."""
    calls = []
    original = app.update_char_count
    app.update_char_count = lambda: (calls.append(1), original())

    app.input.insert("1.0", "abc")
    app.root.update()

    assert 0 < len(calls) <= 3


# ---------------------------------------------------------------- copy

def copy_button_label(app, section_index):
    section = app.body.winfo_children()[section_index]
    toolbar = section.winfo_children()[0]
    return toolbar.winfo_children()[0].winfo_children()[0]


def test_copy_puts_raw_bits_on_the_clipboard(app):
    analyzed(app)
    label = copy_button_label(app, 4)          # ENCODED section
    label.event_generate("<Button-1>")
    app.root.update()

    assert app.root.clipboard_get() == "11111010100000"
    assert label.cget("text") == "COPIED"


def test_copy_with_nothing_analyzed_leaves_the_clipboard_alone(app):
    app.root.clipboard_clear()
    app.root.clipboard_append("USER-CLIPBOARD")

    label = copy_button_label(app, 4)
    label.event_generate("<Button-1>")
    app.root.update()

    assert app.root.clipboard_get() == "USER-CLIPBOARD"


# ---------------------------------------------------------------- sorting

def test_natural_order_is_frequency_descending(app):
    analyzed(app)
    assert table_column(app, "frequency") == ["4", "3", "2"]


def test_sort_toggles_and_marks_the_heading(app):
    analyzed(app)

    app._sort_by("frequency")
    assert table_column(app, "frequency") == ["2", "3", "4"]
    assert app.table.heading("frequency")["text"].endswith("▲")

    app._sort_by("frequency")
    assert table_column(app, "frequency") == ["4", "3", "2"]
    assert app.table.heading("frequency")["text"].endswith("▼")


def test_sort_is_numeric_not_lexical(app):
    analyzed(app)
    app._sort_by("code")
    assert table_column(app, "code") == ["0", "10", "11"]


def test_sorting_one_column_clears_the_other_arrows(app):
    analyzed(app)
    app._sort_by("frequency")
    app._sort_by("code")
    heading = app.table.heading("frequency")["text"]
    assert "▲" not in heading and "▼" not in heading


def test_rerender_clears_the_sort_indicator(app):
    analyzed(app)
    app._sort_by("frequency")
    analyzed(app)
    from app import COLUMN_SPECS
    assert all(
        "▲" not in app.table.heading(name)["text"]
        and "▼" not in app.table.heading(name)["text"]
        for name, _, _ in COLUMN_SPECS
    )


def test_leading_zero_codes_survive_the_table(app):
    analyzed(app, "hello world")
    codes = table_column(app, "code")
    assert any(c.startswith("0") and len(c) > 1 for c in codes)


# ---------------------------------------------------------------- theming

def test_no_widget_falls_back_to_an_os_colour(app):
    """Regression: unset foregrounds resolve to systemTextColor, which is pure
    white in macOS dark mode -- invisible against these light backgrounds."""
    findings = []

    def walk(widget):
        for option in ("bg", "fg"):
            try:
                value = str(widget.cget(option))
            except Exception:
                continue
            if value.startswith("system"):
                findings.append(f"{widget.winfo_class()} {option}={value}")
        if widget.winfo_class() == "Button":
            findings.append("native tk.Button ignores bg on macOS")
        for child in widget.winfo_children():
            walk(child)

    walk(app.root)
    assert not findings, findings
