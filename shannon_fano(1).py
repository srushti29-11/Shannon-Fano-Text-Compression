import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import math

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# SHANNON-FANO CODING ALGORITHM
# ============================================================

def generate_shannon_fano_codes(symbols):
    """
    Generate Shannon-Fano codes for symbols sorted by frequency.
    symbols = [(character, frequency), ...]
    """

    codes = {symbol: "" for symbol, freq in symbols}

    def divide(items):
        if len(items) <= 1:
            return

        total = sum(freq for symbol, freq in items)

        running_sum = 0
        split_index = 0
        minimum_difference = float("inf")

        for i in range(len(items) - 1):
            running_sum += items[i][1]

            difference = abs(total - 2 * running_sum)

            if difference < minimum_difference:
                minimum_difference = difference
                split_index = i

        left = items[:split_index + 1]
        right = items[split_index + 1:]

        for symbol, freq in left:
            codes[symbol] += "0"

        for symbol, freq in right:
            codes[symbol] += "1"

        divide(left)
        divide(right)

    divide(symbols)

    # If there is only one unique character
    if len(symbols) == 1:
        codes[symbols[0][0]] = "0"

    return codes


# ============================================================
# GLOBAL VARIABLES
# ============================================================

current_codes = {}
current_frequency = {}
current_text = ""


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()

window.title("Shannon-Fano Text Compression")
window.geometry("1100x800")
window.minsize(850, 600)

window.configure(bg="#f4f6f8")


# ============================================================
# SCROLLABLE MAIN AREA
# ============================================================

outer_frame = tk.Frame(window, bg="#f4f6f8")
outer_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(
    outer_frame,
    bg="#f4f6f8",
    highlightthickness=0
)

scrollbar = ttk.Scrollbar(
    outer_frame,
    orient="vertical",
    command=canvas.yview
)

canvas.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side="right",
    fill="y"
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

main_frame = tk.Frame(
    canvas,
    bg="#f4f6f8"
)

canvas_window = canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)


def update_scroll_region(event=None):
    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


def resize_main_frame(event):
    canvas.itemconfig(
        canvas_window,
        width=event.width
    )


main_frame.bind(
    "<Configure>",
    update_scroll_region
)

canvas.bind(
    "<Configure>",
    resize_main_frame
)


# ============================================================
# HEADER
# ============================================================

header_frame = tk.Frame(
    main_frame,
    bg="#1f2937",
    padx=25,
    pady=22
)

header_frame.pack(
    fill="x",
    padx=20,
    pady=(20, 10)
)

title_label = tk.Label(
    header_frame,
    text="SHANNON-FANO TEXT COMPRESSION",
    font=("Arial", 24, "bold"),
    bg="#1f2937",
    fg="white"
)

title_label.pack()

subtitle_label = tk.Label(
    header_frame,
    text="Lossless Text Compression & Analysis Tool",
    font=("Arial", 11),
    bg="#1f2937",
    fg="#d1d5db"
)

subtitle_label.pack(
    pady=(6, 0)
)


# ============================================================
# INPUT SECTION
# ============================================================

input_section = tk.LabelFrame(
    main_frame,
    text="  INPUT TEXT  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=15
)

input_section.pack(
    fill="x",
    padx=20,
    pady=10
)


input_text = tk.Text(
    input_section,
    height=6,
    wrap="word",
    font=("Arial", 12),
    relief="solid",
    bd=1
)

input_text.pack(
    fill="x",
    expand=True
)


button_frame = tk.Frame(
    input_section,
    bg="white"
)

button_frame.pack(
    pady=15
)


# ============================================================
# RESULT CARDS
# ============================================================

results_section = tk.LabelFrame(
    main_frame,
    text="  COMPRESSION ANALYSIS  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=15
)

results_section.pack(
    fill="x",
    padx=20,
    pady=10
)


cards_frame = tk.Frame(
    results_section,
    bg="white"
)

cards_frame.pack(
    fill="x"
)


def create_card(parent, title):
    frame = tk.Frame(
        parent,
        bg="#eef2f7",
        padx=15,
        pady=12,
        relief="solid",
        bd=1
    )

    frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    title_label = tk.Label(
        frame,
        text=title,
        font=("Arial", 10, "bold"),
        bg="#eef2f7",
        fg="#4b5563"
    )

    title_label.pack()

    value_label = tk.Label(
        frame,
        text="--",
        font=("Arial", 17, "bold"),
        bg="#eef2f7",
        fg="#111827"
    )

    value_label.pack(
        pady=(5, 0)
    )

    return value_label


original_value = create_card(
    cards_frame,
    "ORIGINAL SIZE"
)

compressed_value = create_card(
    cards_frame,
    "COMPRESSED SIZE"
)

space_saved_value = create_card(
    cards_frame,
    "SPACE SAVED"
)

efficiency_value = create_card(
    cards_frame,
    "CODING EFFICIENCY"
)


# ============================================================
# SECOND ROW OF RESULTS
# ============================================================

second_cards_frame = tk.Frame(
    results_section,
    bg="white"
)

second_cards_frame.pack(
    fill="x",
    pady=(10, 0)
)


entropy_value = create_card(
    second_cards_frame,
    "ENTROPY"
)

average_length_value = create_card(
    second_cards_frame,
    "AVERAGE CODE LENGTH"
)

unique_chars_value = create_card(
    second_cards_frame,
    "UNIQUE CHARACTERS"
)


# ============================================================
# SHANNON-FANO CODE TABLE
# ============================================================

code_section = tk.LabelFrame(
    main_frame,
    text="  SHANNON-FANO CODES  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=15
)

code_section.pack(
    fill="x",
    padx=20,
    pady=10
)


table_frame = tk.Frame(
    code_section,
    bg="white"
)

table_frame.pack(
    fill="both",
    expand=True
)


columns = (
    "character",
    "frequency",
    "probability",
    "code",
    "length"
)

code_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

code_table.heading(
    "character",
    text="Character"
)

code_table.heading(
    "frequency",
    text="Frequency"
)

code_table.heading(
    "probability",
    text="Probability"
)

code_table.heading(
    "code",
    text="Shannon-Fano Code"
)

code_table.heading(
    "length",
    text="Code Length"
)


code_table.column(
    "character",
    width=130,
    anchor="center"
)

code_table.column(
    "frequency",
    width=120,
    anchor="center"
)

code_table.column(
    "probability",
    width=140,
    anchor="center"
)

code_table.column(
    "code",
    width=200,
    anchor="center"
)

code_table.column(
    "length",
    width=120,
    anchor="center"
)


table_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=code_table.yview
)

code_table.configure(
    yscrollcommand=table_scrollbar.set
)

code_table.pack(
    side="left",
    fill="both",
    expand=True
)

table_scrollbar.pack(
    side="right",
    fill="y"
)


# ============================================================
# ENCODED DATA SECTION
# ============================================================

encoded_section = tk.LabelFrame(
    main_frame,
    text="  ENCODED / COMPRESSED DATA  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=15
)

encoded_section.pack(
    fill="x",
    padx=20,
    pady=10
)


encoded_text = tk.Text(
    encoded_section,
    height=7,
    wrap="word",
    font=("Consolas", 10),
    bg="#f8fafc",
    relief="solid",
    bd=1
)

encoded_text.pack(
    fill="x"
)

encoded_text.config(
    state="disabled"
)


# ============================================================
# DECODED TEXT SECTION
# ============================================================

decoded_section = tk.LabelFrame(
    main_frame,
    text="  DECODED TEXT  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=15
)

decoded_section.pack(
    fill="x",
    padx=20,
    pady=10
)


decoded_text = tk.Text(
    decoded_section,
    height=5,
    wrap="word",
    font=("Arial", 11),
    bg="#f8fafc",
    relief="solid",
    bd=1
)

decoded_text.pack(
    fill="x"
)

decoded_text.config(
    state="disabled"
)


# ============================================================
# FREQUENCY GRAPH
# ============================================================

frequency_section = tk.LabelFrame(
    main_frame,
    text="  CHARACTER FREQUENCY DISTRIBUTION  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=10,
    pady=10
)

frequency_section.pack(
    fill="both",
    padx=20,
    pady=10
)


frequency_figure = Figure(
    figsize=(10, 4.8),
    dpi=90
)

frequency_axis = frequency_figure.add_subplot(111)

frequency_axis.set_title(
    "Character Frequency Distribution"
)

frequency_axis.set_xlabel(
    "Characters"
)

frequency_axis.set_ylabel(
    "Frequency"
)


frequency_canvas = FigureCanvasTkAgg(
    frequency_figure,
    master=frequency_section
)

frequency_canvas.draw()

frequency_canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ============================================================
# COMPARISON GRAPH
# ============================================================

comparison_section = tk.LabelFrame(
    main_frame,
    text="  ORIGINAL VS COMPRESSED SIZE  ",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=10,
    pady=10
)

comparison_section.pack(
    fill="both",
    padx=20,
    pady=10
)


comparison_figure = Figure(
    figsize=(10, 4.5),
    dpi=90
)

comparison_axis = comparison_figure.add_subplot(111)

comparison_axis.set_title(
    "Original vs Compressed Data Size"
)

comparison_axis.set_ylabel(
    "Size (bits)"
)


comparison_canvas = FigureCanvasTkAgg(
    comparison_figure,
    master=comparison_section
)

comparison_canvas.draw()

comparison_canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ============================================================
# ENCODE FUNCTION
# ============================================================

def encode_text(text, codes):
    return "".join(
        codes[character]
        for character in text
    )


# ============================================================
# DECODE FUNCTION
# ============================================================

def decode_text(encoded, codes):

    reverse_codes = {
        code: character
        for character, code in codes.items()
    }

    current_code = ""
    decoded = ""

    for bit in encoded:

        current_code += bit

        if current_code in reverse_codes:
            decoded += reverse_codes[current_code]
            current_code = ""

    return decoded


# ============================================================
# UPDATE FREQUENCY GRAPH
# ============================================================

def update_frequency_graph(frequency):

    frequency_axis.clear()

    characters = list(frequency.keys())
    values = list(frequency.values())

    labels = []

    for character in characters:

        if character == " ":
            labels.append("[SPACE]")
        elif character == "\n":
            labels.append("[ENTER]")
        elif character == "\t":
            labels.append("[TAB]")
        else:
            labels.append(character)

    bars = frequency_axis.bar(
        labels,
        values
    )

    frequency_axis.set_title(
        "Character Frequency Distribution"
    )

    frequency_axis.set_xlabel(
        "Characters"
    )

    frequency_axis.set_ylabel(
        "Frequency"
    )

    frequency_axis.tick_params(
        axis="x",
        rotation=45
    )

    for bar, value in zip(bars, values):

        frequency_axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.05,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9
        )

    frequency_figure.tight_layout()

    frequency_canvas.draw()


# ============================================================
# UPDATE COMPARISON GRAPH
# ============================================================

def update_comparison_graph(original_size, compressed_size):

    comparison_axis.clear()

    labels = [
        "Original",
        "Compressed"
    ]

    values = [
        original_size,
        compressed_size
    ]

    bars = comparison_axis.bar(
        labels,
        values
    )

    comparison_axis.set_title(
        "Original vs Compressed Data Size"
    )

    comparison_axis.set_ylabel(
        "Size (bits)"
    )

    for bar, value in zip(bars, values):

        comparison_axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(original_size * 0.02, 1),
            f"{value} bits",
            ha="center",
            va="bottom",
            fontweight="bold"
        )

    comparison_figure.tight_layout()

    comparison_canvas.draw()


# ============================================================
# COMPRESS & ANALYZE
# ============================================================

def compress_and_analyze():

    global current_codes
    global current_frequency
    global current_text

    text = input_text.get(
        "1.0",
        tk.END
    ).rstrip("\n")

    if not text:

        messagebox.showwarning(
            "No Input",
            "Please enter some text first."
        )

        return

    current_text = text

    # Character frequency
    frequency = Counter(text)

    current_frequency = frequency

    # Sort by decreasing frequency
    symbols = sorted(
        frequency.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Generate Shannon-Fano codes
    codes = generate_shannon_fano_codes(
        symbols
    )

    current_codes = codes

    # Encode text
    encoded = encode_text(
        text,
        codes
    )

    # Decode text
    decoded = decode_text(
        encoded,
        codes
    )

    # --------------------------------------------------------
    # SIZE CALCULATIONS
    # --------------------------------------------------------

    original_size = len(text) * 8

    compressed_size = len(encoded)

    if original_size > 0:

        space_saved = (
            (original_size - compressed_size)
            / original_size
        ) * 100

    else:
        space_saved = 0

    # --------------------------------------------------------
    # PROBABILITY
    # --------------------------------------------------------

    total_characters = len(text)

    probabilities = {
        character: freq / total_characters
        for character, freq in frequency.items()
    }

    # --------------------------------------------------------
    # ENTROPY
    # --------------------------------------------------------

    entropy = 0

    for probability in probabilities.values():

        entropy -= (
            probability
            * math.log2(probability)
        )

    # --------------------------------------------------------
    # AVERAGE CODE LENGTH
    # --------------------------------------------------------

    average_length = 0

    for character, probability in probabilities.items():

        average_length += (
            probability
            * len(codes[character])
        )

    # --------------------------------------------------------
    # CODING EFFICIENCY
    # --------------------------------------------------------

    if average_length > 0:

        efficiency = (
            entropy / average_length
        ) * 100

    else:
        efficiency = 0

    # --------------------------------------------------------
    # UPDATE RESULT CARDS
    # --------------------------------------------------------

    original_value.config(
        text=f"{original_size} bits"
    )

    compressed_value.config(
        text=f"{compressed_size} bits"
    )

    space_saved_value.config(
        text=f"{space_saved:.2f}%"
    )

    efficiency_value.config(
        text=f"{efficiency:.2f}%"
    )

    entropy_value.config(
        text=f"{entropy:.3f} bits"
    )

    average_length_value.config(
        text=f"{average_length:.3f} bits"
    )

    unique_chars_value.config(
        text=str(len(frequency))
    )

    # --------------------------------------------------------
    # UPDATE TABLE
    # --------------------------------------------------------

    for item in code_table.get_children():

        code_table.delete(item)

    for character, freq in symbols:

        probability = (
            freq / total_characters
        )

        if character == " ":
            display_character = "[SPACE]"
        elif character == "\n":
            display_character = "[ENTER]"
        elif character == "\t":
            display_character = "[TAB]"
        else:
            display_character = character

        code_table.insert(
            "",
            "end",
            values=(
                display_character,
                freq,
                f"{probability:.4f}",
                codes[character],
                len(codes[character])
            )
        )

    # --------------------------------------------------------
    # UPDATE ENCODED TEXT
    # --------------------------------------------------------

    encoded_text.config(
        state="normal"
    )

    encoded_text.delete(
        "1.0",
        tk.END
    )

    encoded_text.insert(
        tk.END,
        encoded
    )

    encoded_text.config(
        state="disabled"
    )

    # --------------------------------------------------------
    # UPDATE DECODED TEXT
    # --------------------------------------------------------

    decoded_text.config(
        state="normal"
    )

    decoded_text.delete(
        "1.0",
        tk.END
    )

    decoded_text.insert(
        tk.END,
        decoded
    )

    decoded_text.config(
        state="disabled"
    )

    # --------------------------------------------------------
    # UPDATE GRAPHS
    # --------------------------------------------------------

    update_frequency_graph(
        frequency
    )

    update_comparison_graph(
        original_size,
        compressed_size
    )

    # --------------------------------------------------------
    # CHECK LOSSLESS PROPERTY
    # --------------------------------------------------------

    if decoded == text:

        messagebox.showinfo(
            "Analysis Complete",
            "Text compression and decompression completed.\n\n"
            "The decoded text matches the original text."
        )

    else:

        messagebox.showerror(
            "Error",
            "Decoded text does not match the original text."
        )


# ============================================================
# CLEAR FUNCTION
# ============================================================

def clear_all():

    global current_codes
    global current_frequency
    global current_text

    current_codes = {}
    current_frequency = {}
    current_text = ""

    input_text.delete(
        "1.0",
        tk.END
    )

    encoded_text.config(
        state="normal"
    )

    encoded_text.delete(
        "1.0",
        tk.END
    )

    encoded_text.config(
        state="disabled"
    )

    decoded_text.config(
        state="normal"
    )

    decoded_text.delete(
        "1.0",
        tk.END
    )

    decoded_text.config(
        state="disabled"
    )

    for item in code_table.get_children():

        code_table.delete(item)

    # Reset result cards
    original_value.config(text="--")
    compressed_value.config(text="--")
    space_saved_value.config(text="--")
    efficiency_value.config(text="--")
    entropy_value.config(text="--")
    average_length_value.config(text="--")
    unique_chars_value.config(text="--")

    # Clear frequency graph
    frequency_axis.clear()

    frequency_axis.set_title(
        "Character Frequency Distribution"
    )

    frequency_axis.set_xlabel(
        "Characters"
    )

    frequency_axis.set_ylabel(
        "Frequency"
    )

    frequency_canvas.draw()

    # Clear comparison graph
    comparison_axis.clear()

    comparison_axis.set_title(
        "Original vs Compressed Data Size"
    )

    comparison_axis.set_ylabel(
        "Size (bits)"
    )

    comparison_canvas.draw()


# ============================================================
# BUTTONS
# ============================================================

compress_button = tk.Button(
    button_frame,
    text="COMPRESS & ANALYZE",
    command=compress_and_analyze,
    font=("Arial", 11, "bold"),
    padx=20,
    pady=10,
    bg="#2563eb",
    fg="white",
    relief="flat",
    cursor="hand2"
)

compress_button.pack(
    side="left",
    padx=8
)


clear_button = tk.Button(
    button_frame,
    text="CLEAR",
    command=clear_all,
    font=("Arial", 11, "bold"),
    padx=25,
    pady=10,
    bg="#6b7280",
    fg="white",
    relief="flat",
    cursor="hand2"
)

clear_button.pack(
    side="left",
    padx=8
)


# ============================================================
# FOOTER
# ============================================================

footer = tk.Label(
    main_frame,
    text="Shannon-Fano Coding • Lossless Text Compression",
    font=("Arial", 9),
    bg="#f4f6f8",
    fg="#6b7280",
    pady=15
)

footer.pack()


# ============================================================
# START APPLICATION
# ============================================================

window.mainloop()
