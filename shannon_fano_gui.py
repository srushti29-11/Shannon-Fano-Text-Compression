import tkinter as tk
from tkinter import ttk, messagebox

from shannon_fano_core import analyze


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()
root.title("Shannon-Fano Coding - Transmitter and Receiver")
root.geometry("1200x750")
root.minsize(1000, 650)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="SHANNON-FANO CODING",
    font=("Arial", 22, "bold")
)
title.pack(pady=10)

subtitle = tk.Label(
    root,
    text="Source Coding - Transmitter and Receiver",
    font=("Arial", 12)
)
subtitle.pack(pady=(0, 10))


# ============================================================
# MAIN CONTAINER
# ============================================================

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=15, pady=10)

# ---------------- TRANSMITTER ----------------

transmitter_frame = tk.LabelFrame(
    main_frame,
    text=" TRANSMITTER ",
    font=("Arial", 14, "bold"),
    padx=10,
    pady=10
)

transmitter_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 7)
)

# ---------------- RECEIVER ----------------

receiver_frame = tk.LabelFrame(
    main_frame,
    text=" RECEIVER ",
    font=("Arial", 14, "bold"),
    padx=10,
    pady=10
)

receiver_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(7, 0)
)


# ============================================================
# TRANSMITTER
# ============================================================

tk.Label(
    transmitter_frame,
    text="Enter Message:",
    font=("Arial", 11, "bold")
).pack(anchor="w")

input_text = tk.Text(
    transmitter_frame,
    height=4,
    font=("Consolas", 11),
    wrap="word"
)

input_text.pack(fill="x", pady=5)


# ---------------- BUTTON ----------------

encode_button = tk.Button(
    transmitter_frame,
    text="GENERATE & TRANSMIT",
    font=("Arial", 11, "bold"),
    command=lambda: process_message()
)

encode_button.pack(pady=8)


# ============================================================
# FREQUENCY TABLE
# ============================================================

tk.Label(
    transmitter_frame,
    text="Character Frequency & Shannon-Fano Code",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(5, 3))

columns = ("character", "frequency", "probability", "code")

table = ttk.Treeview(
    transmitter_frame,
    columns=columns,
    show="headings",
    height=8
)

table.heading("character", text="Character")
table.heading("frequency", text="Frequency")
table.heading("probability", text="Probability")
table.heading("code", text="Code")

table.column("character", width=100, anchor="center")
table.column("frequency", width=80, anchor="center")
table.column("probability", width=100, anchor="center")
table.column("code", width=150, anchor="center")

table.pack(fill="x", pady=5)


# ============================================================
# PARTITION DISPLAY
# ============================================================

tk.Label(
    transmitter_frame,
    text="Shannon-Fano Partitioning:",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(5, 3))

partition_box = tk.Text(
    transmitter_frame,
    height=7,
    font=("Consolas", 9),
    wrap="word"
)

partition_box.pack(fill="both", expand=True)


# ============================================================
# TRANSMITTED DATA
# ============================================================

tk.Label(
    transmitter_frame,
    text="Encoded / Transmitted Data:",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(7, 3))

encoded_box = tk.Text(
    transmitter_frame,
    height=4,
    font=("Consolas", 9),
    wrap="word"
)

encoded_box.pack(fill="x")


# ============================================================
# RECEIVER
# ============================================================

tk.Label(
    receiver_frame,
    text="Received Encoded Data:",
    font=("Arial", 11, "bold")
).pack(anchor="w")

received_box = tk.Text(
    receiver_frame,
    height=6,
    font=("Consolas", 10),
    wrap="word"
)

received_box.pack(fill="x", pady=5)


# ============================================================
# DECODE BUTTON
# ============================================================

decode_button = tk.Button(
    receiver_frame,
    text="RECEIVE & DECODE",
    font=("Arial", 11, "bold"),
    command=lambda: decode_received()
)

decode_button.pack(pady=8)


# ============================================================
# DECODED MESSAGE
# ============================================================

tk.Label(
    receiver_frame,
    text="Decoded / Received Message:",
    font=("Arial", 11, "bold")
).pack(anchor="w")

decoded_box = tk.Text(
    receiver_frame,
    height=5,
    font=("Arial", 11),
    wrap="word"
)

decoded_box.pack(fill="x", pady=5)


# ============================================================
# ANALYSIS RESULTS
# ============================================================

tk.Label(
    receiver_frame,
    text="Transmission Analysis:",
    font=("Arial", 11, "bold")
).pack(anchor="w", pady=(10, 3))

analysis_box = tk.Text(
    receiver_frame,
    height=10,
    font=("Consolas", 10),
    wrap="word"
)

analysis_box.pack(fill="both", expand=True)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

current_result = None


# ============================================================
# CHARACTER DISPLAY
# ============================================================

def display_character(character):

    if character == " ":
        return "[SPACE]"

    if character == "\n":
        return "[ENTER]"

    if character == "\t":
        return "[TAB]"

    return character


# ============================================================
# PARTITION DISPLAY
# ============================================================

def generate_partition_text(symbols):

    steps = []

    def divide(items, prefix=""):

        if len(items) <= 1:
            return

        total = sum(freq for _, freq in items)

        running_sum = 0
        split_index = 0
        minimum_difference = float("inf")

        for i in range(len(items) - 1):

            running_sum += items[i][1]

            difference = abs(
                total - 2 * running_sum
            )

            if difference < minimum_difference:

                minimum_difference = difference
                split_index = i

        left = items[:split_index + 1]
        right = items[split_index + 1:]

        left_text = " ".join(
            f"{display_character(char)}:{freq}"
            for char, freq in left
        )

        right_text = " ".join(
            f"{display_character(char)}:{freq}"
            for char, freq in right
        )

        steps.append(
            f"Partition {len(steps) + 1}\n"
            f"  0 → {left_text}\n"
            f"  1 → {right_text}\n"
        )

        divide(left, prefix + "0")
        divide(right, prefix + "1")

    divide(symbols)

    return "\n".join(steps)


# ============================================================
# TRANSMITTER PROCESS
# ============================================================

def process_message():

    global current_result

    text = input_text.get("1.0", "end-1c")

    if not text:

        messagebox.showwarning(
            "Empty Input",
            "Please enter some text."
        )

        return

    try:

        result = analyze(text)

        current_result = result

        # Clear old data

        for item in table.get_children():
            table.delete(item)

        partition_box.delete("1.0", tk.END)
        encoded_box.delete("1.0", tk.END)
        received_box.delete("1.0", tk.END)
        decoded_box.delete("1.0", tk.END)
        analysis_box.delete("1.0", tk.END)

        # ---------------- FREQUENCY TABLE ----------------

        for character, frequency in result.symbols:

            probability = result.probabilities[character]

            code = result.codes[character]

            table.insert(
                "",
                "end",
                values=(
                    display_character(character),
                    frequency,
                    f"{probability:.4f}",
                    code
                )
            )

        # ---------------- PARTITIONS ----------------

        partition_text = generate_partition_text(
            result.symbols
        )

        partition_box.insert(
            tk.END,
            partition_text
        )

        # ---------------- ENCODED DATA ----------------

        encoded_box.insert(
            tk.END,
            result.encoded
        )

        messagebox.showinfo(
            "Transmission Ready",
            "Message has been encoded successfully.\n"
            "The encoded data is ready for transmission."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )


# ============================================================
# RECEIVER PROCESS
# ============================================================

def decode_received():

    global current_result

    if current_result is None:

        messagebox.showwarning(
            "No Data",
            "First generate the encoded data from the transmitter."
        )

        return

    encoded_data = received_box.get(
        "1.0",
        "end-1c"
    ).replace(" ", "").replace("\n", "")

    if not encoded_data:

        messagebox.showwarning(
            "No Received Data",
            "Please enter or transmit encoded data."
        )

        return

    try:

        # Decode using Shannon-Fano codes

        reverse_codes = {
            code: character
            for character, code in current_result.codes.items()
        }

        current_code = ""
        decoded = []

        for bit in encoded_data:

            if bit not in "01":

                raise ValueError(
                    "Encoded data must contain only 0 and 1."
                )

            current_code += bit

            if current_code in reverse_codes:

                decoded.append(
                    reverse_codes[current_code]
                )

                current_code = ""

        decoded_text = "".join(decoded)

        # ---------------- DISPLAY ----------------

        decoded_box.delete(
            "1.0",
            tk.END
        )

        decoded_box.insert(
            tk.END,
            decoded_text
        )

        # ---------------- ANALYSIS ----------------

        analysis_box.delete(
            "1.0",
            tk.END
        )

        lossless = (
            decoded_text == current_result.text
        )

        analysis_text = (
            f"Original Size       : "
            f"{current_result.original_size} bits\n\n"

            f"Compressed Size     : "
            f"{current_result.compressed_size} bits\n\n"

            f"Entropy             : "
            f"{current_result.entropy:.4f} bits/symbol\n\n"

            f"Average Code Length : "
            f"{current_result.average_length:.4f} bits/symbol\n\n"

            f"Coding Efficiency   : "
            f"{current_result.efficiency:.2f}%\n\n"

            f"Space Saved         : "
            f"{current_result.space_saved:.2f}%\n\n"

            f"Transmission Status : "
            f"{'LOSSLESS ✓' if lossless else 'ERROR ✗'}"
        )

        analysis_box.insert(
            tk.END,
            analysis_text
        )

        messagebox.showinfo(
            "Receiver",
            "Encoded data decoded successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Decoding Error",
            str(error)
        )


# ============================================================
# AUTO COPY TRANSMITTER → RECEIVER
# ============================================================

def transmit_data():

    if current_result is None:
        return

    received_box.delete(
        "1.0",
        tk.END
    )

    received_box.insert(
        tk.END,
        current_result.encoded
    )


# ============================================================
# TRANSMIT BUTTON
# ============================================================

transmit_button = tk.Button(
    transmitter_frame,
    text="SEND DATA →",
    font=("Arial", 10, "bold"),
    command=transmit_data
)

transmit_button.pack(
    pady=5
)


# ============================================================
# START GUI
# ============================================================

root.mainloop()
  
