import tkinter as tk
from tkinter import messagebox
from collections import Counter
import math


# ---------------- SHANNON-FANO CODING ----------------

def generate_codes(symbols):
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

    # Handle input containing only one unique character
    if len(symbols) == 1:
        codes[symbols[0][0]] = "0"

    return codes


# ---------------- ENCODING ----------------

def encode_text(text, codes):
    return "".join(codes[ch] for ch in text)


# ---------------- DECODING ----------------

def decode_text(encoded_text, codes):
    reverse_codes = {code: symbol for symbol, code in codes.items()}

    decoded = ""
    current = ""

    for bit in encoded_text:
        current += bit

        if current in reverse_codes:
            decoded += reverse_codes[current]
            current = ""

    return decoded


# ---------------- MAIN PROCESS ----------------

def process_text():
    text = input_text.get("1.0", tk.END).rstrip("\n")

    if not text:
        messagebox.showwarning("Warning", "Please enter some text.")
        return

    frequency = Counter(text)

    symbols = sorted(
        frequency.items(),
        key=lambda item: item[1],
        reverse=True
    )

    codes = generate_codes(symbols)

    encoded = encode_text(text, codes)
    decoded = decode_text(encoded, codes)

    original_bits = len(text) * 8
    compressed_bits = len(encoded)

    compression_ratio = (
        compressed_bits / original_bits
    ) * 100

    space_saving = 100 - compression_ratio

    entropy = 0

    for freq in frequency.values():
        probability = freq / len(text)
        entropy -= probability * math.log2(probability)

    average_code_length = compressed_bits / len(text)

    efficiency = (
        entropy / average_code_length
    ) * 100

    # Clear previous output
    code_table.delete("1.0", tk.END)

    # Display character codes
    code_table.insert(tk.END, "CHARACTER\tFREQUENCY\tCODE\n")
    code_table.insert(tk.END, "-" * 40 + "\n")

    for character, freq in symbols:

        if character == " ":
            display = "[SPACE]"
        elif character == "\n":
            display = "[NEWLINE]"
        else:
            display = character

        code_table.insert(
            tk.END,
            f"{display}\t\t{freq}\t\t{codes[character]}\n"
        )

    # Display results
    encoded_output.delete("1.0", tk.END)
    encoded_output.insert(tk.END, encoded)

    decoded_output.delete("1.0", tk.END)
    decoded_output.insert(tk.END, decoded)

    results_label.config(
        text=
        f"Original Size      : {original_bits} bits\n"
        f"Compressed Size    : {compressed_bits} bits\n"
        f"Compression Ratio  : {compression_ratio:.2f}%\n"
        f"Space Saving       : {space_saving:.2f}%\n"
        f"Coding Efficiency  : {efficiency:.2f}%"
    )


# ---------------- GUI DESIGN ----------------

window = tk.Tk()
window.title("Shannon-Fano Text Compression")
window.geometry("900x750")

title = tk.Label(
    window,
    text="SHANNON-FANO TEXT COMPRESSION",
    font=("Arial", 20, "bold")
)

title.pack(pady=15)


# Input section
tk.Label(
    window,
    text="Enter Text:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

input_text = tk.Text(
    window,
    height=5,
    width=100
)

input_text.pack(padx=20, pady=5)


# Button
process_button = tk.Button(
    window,
    text="COMPRESS & ANALYZE",
    command=process_text,
    font=("Arial", 11, "bold"),
    padx=15,
    pady=8
)

process_button.pack(pady=10)


# Code table
tk.Label(
    window,
    text="Shannon-Fano Codes:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

code_table = tk.Text(
    window,
    height=10,
    width=100
)

code_table.pack(padx=20, pady=5)


# Encoded text
tk.Label(
    window,
    text="Encoded / Compressed Data:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

encoded_output = tk.Text(
    window,
    height=4,
    width=100
)

encoded_output.pack(padx=20, pady=5)


# Decoded text
tk.Label(
    window,
    text="Decoded Text:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

decoded_output = tk.Text(
    window,
    height=3,
    width=100
)

decoded_output.pack(padx=20, pady=5)


# Results
tk.Label(
    window,
    text="Compression Results:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

results_label = tk.Label(
    window,
    text="Enter text and click the button.",
    font=("Arial", 11),
    justify="left"
)

results_label.pack(anchor="w", padx=20, pady=8)


window.mainloop()
