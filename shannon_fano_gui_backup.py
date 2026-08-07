# Shannon-Fano Coding for Text Compression

from collections import Counter
import math


# Generate Shannon-Fano codes
def shannon_fano(symbols):
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

        # Assign binary values
        for symbol, freq in left:
            codes[symbol] += "0"

        for symbol, freq in right:
            codes[symbol] += "1"

        divide(left)
        divide(right)

    divide(symbols)
    return codes


# Encode the text
def encode_text(text, codes):
    return "".join(codes[character] for character in text)


# Decode the encoded data
def decode_text(encoded_text, codes):
    reverse_codes = {code: symbol for symbol, code in codes.items()}

    decoded_text = ""
    current_code = ""

    for bit in encoded_text:
        current_code += bit

        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""

    return decoded_text


# Main program
text = input("Enter text to compress: ")

if text.strip() == "":
    print("Please enter some text.")
else:
    # Calculate frequency
    frequency = Counter(text)

    # Sort symbols by frequency in descending order
    symbols = sorted(
        frequency.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Generate Shannon-Fano codes
    codes = shannon_fano(symbols)

    # Encode and decode
    encoded_text = encode_text(text, codes)
    decoded_text = decode_text(encoded_text, codes)

    # Calculate sizes
    original_bits = len(text) * 8
    compressed_bits = len(encoded_text)

    # Compression ratio
    compression_ratio = (
        compressed_bits / original_bits
    ) * 100

    # Coding efficiency
    entropy = 0

    for freq in frequency.values():
        probability = freq / len(text)
        entropy -= probability * math.log2(probability)

    average_code_length = compressed_bits / len(text)

    efficiency = (
        entropy / average_code_length
    ) * 100

    # Display results
    print("\n--- Character Frequencies ---")

    for character, freq in symbols:
        display_character = character

        if character == " ":
            display_character = "[SPACE]"
        elif character == "\n":
            display_character = "[NEWLINE]"

        print(f"{display_character} : {freq}")

    print("\n--- Shannon-Fano Codes ---")

    for character, freq in symbols:
        display_character = character

        if character == " ":
            display_character = "[SPACE]"
        elif character == "\n":
            display_character = "[NEWLINE]"

        print(f"{display_character} : {codes[character]}")

    print("\n--- Results ---")
    print("Original Text    :", text)
    print("Encoded Text     :", encoded_text)
    print("Decoded Text     :", decoded_text)
    print("Original Size    :", original_bits, "bits")
    print("Compressed Size  :", compressed_bits, "bits")
    print("Compression      :", round(compression_ratio, 2), "%")
    print("Coding Efficiency:", round(efficiency, 2), "%")
