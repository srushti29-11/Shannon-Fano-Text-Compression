"""Shannon-Fano text compression - simple GUI.

A lighter alternative to app.py. Colours are left unset here so every widget
follows the OS appearance consistently.
"""

import tkinter as tk
from tkinter import messagebox

from shannon_fano_core import analyze, display_character


# ---------------- MAIN PROCESS ----------------

def process_text():
    text = input_text.get("1.0", tk.END).rstrip("\n")

    if not text:
        messagebox.showwarning("Warning", "Please enter some text.")
        return

    result = analyze(text)

    # Clear previous output
    code_table.delete("1.0", tk.END)

    code_table.insert(tk.END, "CHARACTER\tFREQUENCY\tCODE\n")
    code_table.insert(tk.END, "-" * 40 + "\n")

    for character, freq in result.symbols:
        code_table.insert(
            tk.END,
            f"{display_character(character)}\t\t{freq}\t\t"
            f"{result.codes[character]}\n"
        )

    encoded_output.delete("1.0", tk.END)
    encoded_output.insert(tk.END, result.encoded)

    decoded_output.delete("1.0", tk.END)
    decoded_output.insert(tk.END, result.decoded)

    compression_ratio = 100 - result.space_saved

    results_label.config(
        text=
        f"Original Size      : {result.original_size} bits\n"
        f"Compressed Size    : {result.compressed_size} bits\n"
        f"Compression Ratio  : {compression_ratio:.2f}%\n"
        f"Space Saving       : {result.space_saved:.2f}%\n"
        f"Coding Efficiency  : {result.efficiency:.2f}%"
    )


# ---------------- GUI DESIGN ----------------

window = tk.Tk()
window.title("Shannon-Fano Text Compression")
window.geometry("900x750")

tk.Label(
    window,
    text="SHANNON-FANO TEXT COMPRESSION",
    font=("Arial", 20, "bold")
).pack(pady=15)


# Input section
tk.Label(
    window,
    text="Enter Text:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

input_text = tk.Text(window, height=5, width=100)
input_text.pack(padx=20, pady=5)


# Button
tk.Button(
    window,
    text="COMPRESS & ANALYZE",
    command=process_text,
    font=("Arial", 11, "bold"),
    padx=15,
    pady=8
).pack(pady=10)


# Code table
tk.Label(
    window,
    text="Shannon-Fano Codes:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

code_table = tk.Text(window, height=10, width=100)
code_table.pack(padx=20, pady=5)


# Encoded text
tk.Label(
    window,
    text="Encoded / Compressed Data:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

encoded_output = tk.Text(window, height=4, width=100)
encoded_output.pack(padx=20, pady=5)


# Decoded text
tk.Label(
    window,
    text="Decoded Text:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=20)

decoded_output = tk.Text(window, height=3, width=100)
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


if __name__ == "__main__":
    window.mainloop()
