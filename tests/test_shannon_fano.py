"""Tests for shannon_fano_core.

These replace the runtime self-check that used to live in the GUI as a
messagebox -- an assertion that could only ever fire on an end user's screen.
"""

import itertools
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shannon_fano_core import (  # noqa: E402
    analyze,
    decode_text,
    display_character,
    encode_text,
    generate_shannon_fano_codes,
    group_bits,
)


ROUNDTRIP_CASES = [
    pytest.param("a", id="single-character"),
    pytest.param("aaaa", id="all-identical"),
    pytest.param("ab", id="two-symbols"),
    pytest.param("AABBBCCCC", id="spec-example"),
    pytest.param("hello world", id="with-space"),
    pytest.param("line one\nline two\ttabbed", id="whitespace"),
    pytest.param("   ", id="spaces-only"),
    pytest.param("éàü 你好 \U0001f600\U0001f600", id="unicode"),
    pytest.param("the quick brown fox jumps over the lazy dog", id="pangram"),
    pytest.param("z" * 1000, id="long-repeat"),
    pytest.param("".join(chr(32 + i % 95) for i in range(500)), id="wide-alphabet"),
]


@pytest.mark.parametrize("text", ROUNDTRIP_CASES)
def test_roundtrip_is_lossless(text):
    result = analyze(text)
    assert result.decoded == text
    assert result.is_lossless


@pytest.mark.parametrize("text", ROUNDTRIP_CASES)
def test_codes_are_prefix_free(text):
    codes = analyze(text).codes.values()
    for a, b in itertools.permutations(codes, 2):
        assert not a.startswith(b), f"{a!r} has prefix {b!r}"


@pytest.mark.parametrize("text", ROUNDTRIP_CASES)
def test_every_symbol_gets_a_nonempty_code(text):
    result = analyze(text)
    assert set(result.codes) == set(result.frequency)
    assert all(code for code in result.codes.values())


def test_single_symbol_gets_code_zero():
    """The degenerate case: one distinct character has no path in the tree.

    The older implementations returned an empty code here, which made
    average_length 0.0 and crashed with ZeroDivisionError.
    """
    result = analyze("aaaa")
    assert result.codes == {"a": "0"}
    assert result.encoded == "0000"
    assert result.average_length == 1.0
    assert result.entropy == 0.0
    assert f"{result.entropy:.3f}" == "0.000"  # not "-0.000"
    assert result.efficiency == 0.0


def test_spec_example_matches_documented_values():
    """Values published in the project PDF for AABBBCCCC."""
    result = analyze("AABBBCCCC")

    assert result.symbols == [("C", 4), ("B", 3), ("A", 2)]
    assert result.codes == {"C": "0", "B": "10", "A": "11"}

    assert result.encoded == "11111010100000"
    assert result.compressed_size == 14
    assert result.original_size == 72

    assert round(result.entropy, 4) == 1.5305
    assert round(result.average_length, 4) == 1.5556
    assert round(result.efficiency, 2) == 98.39


def test_entropy_matches_direct_formula():
    text = "the quick brown fox jumps over the lazy dog"
    result = analyze(text)
    expected = math.fsum(
        -p * math.log2(p) for p in result.probabilities.values()
    )
    assert result.entropy == pytest.approx(expected, abs=1e-12)


def test_average_length_matches_encoded_size():
    """Sum of p*len(code) is by definition len(encoded)/len(text)."""
    text = "shannon fano coding is a lossless compression technique"
    result = analyze(text)
    assert result.average_length == pytest.approx(
        result.compressed_size / len(text), abs=1e-12
    )


def test_space_saved_is_consistent_with_sizes():
    result = analyze("AABBBCCCC")
    expected = (
        (result.original_size - result.compressed_size) / result.original_size
    ) * 100
    assert result.space_saved == pytest.approx(expected)


def test_symbols_are_sorted_by_decreasing_frequency():
    result = analyze("aaabbc")
    counts = [freq for _, freq in result.symbols]
    assert counts == sorted(counts, reverse=True)


def test_more_frequent_symbols_are_not_longer():
    result = analyze("the quick brown fox jumps over the lazy dog")
    lengths = [len(result.codes[ch]) for ch, _ in result.symbols]
    assert lengths[0] <= lengths[-1]


def test_analyze_rejects_empty_text():
    with pytest.raises(ValueError):
        analyze("")


def test_generate_codes_handles_empty_symbol_list():
    assert generate_shannon_fano_codes([]) == {}


def test_encode_decode_are_inverse_with_explicit_codes():
    codes = {"C": "0", "B": "10", "A": "11"}
    encoded = encode_text("AABBBCCCC", codes)
    assert encoded == "11111010100000"
    assert decode_text(encoded, codes) == "AABBBCCCC"


@pytest.mark.parametrize("character,expected", [
    (" ", "[SPACE]"),
    ("\n", "[ENTER]"),
    ("\t", "[TAB]"),
    ("a", "a"),
    ("你", "你"),
    ("😀", "😀"),
    # Non-printables would otherwise render as an invisible glyph.
    ("\x00", "\\x00"),
    ("\x07", "\\x07"),
    ("\x1b", "\\x1b"),
    ("\x7f", "\\x7f"),
    ("\r", "\\x0d"),
    (chr(0x85), "\\x85"),        # next line -- single byte, so \\xNN
    (chr(0x200B), "U+200B"),     # zero-width space -- above 0xFF
    (chr(0xFEFF), "U+FEFF"),     # byte-order mark
])
def test_display_character(character, expected):
    assert display_character(character) == expected


def test_display_character_never_returns_blank():
    """Every character in the table must show something visible."""
    for codepoint in list(range(0, 0x100)) + [0x200b, 0x2028, 0xfeff]:
        shown = display_character(chr(codepoint))
        assert shown.strip(), f"U+{codepoint:04X} renders as blank {shown!r}"


def test_display_character_does_not_affect_coding():
    """Control characters still round-trip losslessly."""
    text = "".join(chr(i) for i in range(32)) + "abc"
    result = analyze(text)
    assert result.decoded == text
    assert set(result.codes) == set(text)


@pytest.mark.parametrize("bits,expected", [
    ("", ""),
    ("1", "1"),
    ("1111101010000 0".replace(" ", ""), "11111010 100000"),
    ("11111111", "11111111"),                       # exact multiple
    ("111111110", "11111111 0"),                    # one over
    ("1010101010101010", "10101010 10101010"),
])
def test_group_bits(bits, expected):
    assert group_bits(bits) == expected


def test_group_bits_is_display_only():
    """Grouping must not change the data -- stripping spaces restores it."""
    result = analyze("the quick brown fox jumps over the lazy dog")
    grouped = group_bits(result.encoded)
    assert grouped.replace(" ", "") == result.encoded
    assert len(result.encoded) == result.compressed_size


def test_group_bits_custom_size():
    assert group_bits("110011", size=2) == "11 00 11"
    assert group_bits("11001", size=4) == "1100 1"
