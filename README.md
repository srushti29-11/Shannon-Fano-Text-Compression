# Shannon-Fano Text Compression

Microproject on Shannon-Fano coding for lossless text compression.

Enter text, and the app builds a frequency table, generates variable-length
prefix-free codes by recursive partitioning, encodes the text, decodes it back,
and reports the compression statistics with two charts.

## Layout

| File | Purpose |
| --- | --- |
| `shannon_fano_core.py` | The algorithm and all statistics. Imports no UI at all. |
| `theme.py` | Colours, fonts and ttk styling. |
| `widgets.py` | Reusable themed widget factories. |
| `app.py` | Full graphical app — `ShannonFanoApp` (Tkinter + Matplotlib). |
| `shannon_fano_gui.py` | Smaller GUI, no charts. |
| `shannon_fano.py` | Console version. |
| `tests/` | `test_shannon_fano.py` (logic) and `test_app.py` (UI). |

Dependencies run one way only:

```
shannon_fano_core  ←  no UI imports
       ↑
     theme  →  widgets  →  app
```

All three front ends import `shannon_fano_core`, so there is exactly one
implementation of the algorithm.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python app.py              # full GUI
.venv/bin/python shannon_fano_gui.py # simple GUI
.venv/bin/python shannon_fano.py     # console
```

## Test

```bash
.venv/bin/python -m pytest tests/ -v
```

## macOS note

Apple's system Python (`/usr/bin/python3`) links against **Tcl/Tk 8.5.9**, which
is deprecated and does not render Tk-drawn widgets on recent macOS — the window
opens nearly blank, showing only buttons and scrollbars.

Use a Python built against Tk 8.6 or newer:

```bash
brew install python-tk
python3 -m venv .venv   # using the Homebrew python3
```

Check what you have with:

```bash
.venv/bin/python -c "import tkinter; print(tkinter.Tk().tk.call('info','patchlevel'))"
```

## Worked example

Input `AABBBCCCC`:

| Character | Frequency | Probability | Code | Length |
| --- | --- | --- | --- | --- |
| C | 4 | 0.4444 | `0` | 1 |
| B | 3 | 0.3333 | `10` | 2 |
| A | 2 | 0.2222 | `11` | 2 |

Encoded: `11111010100000` (14 bits, vs 72 bits at 8 bits/character)
Entropy 1.5305 bits/symbol, average code length 1.5556, coding efficiency 98.39%.

The bit counts compare the encoded representation against an assumed 8 bits per
character. A real compressed file would also have to store the codebook and pad
to whole bytes, so this is an educational measure rather than a file-size claim.
