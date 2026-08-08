"""Shannon-Fano coding: the algorithm and its metrics.

Pure logic with no GUI dependency, so it can be imported, tested and reused.
Every entry point in this project (app.py, shannon_fano.py, shannon_fano_gui.py)
builds on this module rather than carrying its own copy.
"""

import math
from collections import Counter
from typing import NamedTuple


# ============================================================
# CODE GENERATION
# ============================================================

def generate_shannon_fano_codes(symbols):
    """
    Generate Shannon-Fano codes for symbols sorted by decreasing frequency.
    symbols = [(character, frequency), ...]
    """

    codes = {}

    def divide(items, prefix=""):
        # A single symbol is a leaf, and its code is the path taken to reach
        # it. The whole alphabet being one symbol is the only case with no
        # path, so it gets a single bit.
        if len(items) == 1:
            codes[items[0][0]] = prefix or "0"
            return

        total = sum(freq for _, freq in items)

        running_sum = 0
        split_index = 0
        minimum_difference = float("inf")

        for i in range(len(items) - 1):
            running_sum += items[i][1]

            difference = abs(total - 2 * running_sum)

            if difference < minimum_difference:
                minimum_difference = difference
                split_index = i

        divide(items[:split_index + 1], prefix + "0")
        divide(items[split_index + 1:], prefix + "1")

    if symbols:
        divide(symbols)

    return codes


# ============================================================
# ENCODE / DECODE
# ============================================================

def encode_text(text, codes):
    return "".join(codes[character] for character in text)


def decode_text(encoded, codes):
    """Decode a bit string. Shannon-Fano codes are prefix-free, so the first
    match while reading left to right is always the right one."""

    reverse_codes = {
        code: character
        for character, code in codes.items()
    }

    current_code = ""
    decoded = []

    for bit in encoded:

        current_code += bit

        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ""

    return "".join(decoded)


# ============================================================
# DISPLAY HELPERS
# ============================================================

SPECIAL_CHARACTER_LABELS = {
    " ": "[SPACE]",
    "\n": "[ENTER]",
    "\t": "[TAB]",
}


def display_character(character):
    """Readable stand-in for characters that would otherwise render as blank.

    Display only -- encoding, decoding and every count use the real character,
    so losslessness is unaffected.
    """
    # The named labels must win: "\n".isprintable() is False, so checking
    # printability first would show [ENTER] as \x0a.
    label = SPECIAL_CHARACTER_LABELS.get(character)
    if label:
        return label

    if character.isprintable():
        return character

    codepoint = ord(character)
    return f"\\x{codepoint:02x}" if codepoint <= 0xFF else f"U+{codepoint:04X}"


def group_bits(bits, size=8):
    """Space out a bit string in fixed-size groups so it can be read.

    Presentation only -- the grouped form is never fed back into decode_text,
    and every reported bit count uses the original string.
    """
    return " ".join(bits[i:i + size] for i in range(0, len(bits), size))


# ============================================================
# ANALYSIS
# ============================================================

class AnalysisResult(NamedTuple):
    text: str
    frequency: Counter
    symbols: list
    codes: dict
    encoded: str
    decoded: str
    probabilities: dict
    original_size: int
    compressed_size: int
    space_saved: float
    entropy: float
    average_length: float
    efficiency: float

    @property
    def is_lossless(self):
        return self.decoded == self.text


def analyze(text):
    """Compress `text` and compute every statistic the UI reports.

    Raises ValueError on empty input -- callers decide how to surface that.
    """

    if not text:
        raise ValueError("analyze() requires non-empty text")

    frequency = Counter(text)
    symbols = frequency.most_common()          # sorted by decreasing frequency

    codes = generate_shannon_fano_codes(symbols)
    encoded = encode_text(text, codes)
    decoded = decode_text(encoded, codes)

    total_characters = len(text)
    original_size = total_characters * 8
    compressed_size = len(encoded)

    space_saved = (
        (original_size - compressed_size) / original_size
    ) * 100

    probabilities = {
        character: freq / total_characters
        for character, freq in frequency.items()
    }

    # Negation sits inside the terms so that a single-symbol input sums to
    # +0.0 rather than -0.0, which would display as "-0.000".
    entropy = sum(
        -probability * math.log2(probability)
        for probability in probabilities.values()
    )

    average_length = sum(
        probability * len(codes[character])
        for character, probability in probabilities.items()
    )

    # Every symbol gets at least one bit, so average_length is never zero.
    efficiency = (entropy / average_length) * 100

    return AnalysisResult(
        text=text,
        frequency=frequency,
        symbols=symbols,
        codes=codes,
        encoded=encoded,
        decoded=decoded,
        probabilities=probabilities,
        original_size=original_size,
        compressed_size=compressed_size,
        space_saved=space_saved,
        entropy=entropy,
        average_length=average_length,
        efficiency=efficiency,
    )
