# Shannon-Fano Coding for Text Compression - console version

from shannon_fano_core import analyze, display_character


def main():
    text = input("Enter text to compress: ")

    if not text.strip():
        print("Please enter some text.")
        return

    result = analyze(text)

    print("\n--- Character Frequencies ---")

    for character, freq in result.symbols:
        print(f"{display_character(character)} : {freq}")

    print("\n--- Shannon-Fano Codes ---")

    for character, freq in result.symbols:
        print(f"{display_character(character)} : {result.codes[character]}")

    compression_ratio = 100 - result.space_saved

    print("\n--- Results ---")
    print("Original Text    :", result.text)
    print("Encoded Text     :", result.encoded)
    print("Decoded Text     :", result.decoded)
    print("Original Size    :", result.original_size, "bits")
    print("Compressed Size  :", result.compressed_size, "bits")
    print("Compression      :", round(compression_ratio, 2), "%")
    print("Space Saving     :", round(result.space_saved, 2), "%")
    print("Coding Efficiency:", round(result.efficiency, 2), "%")
    print("Lossless         :", "PASS" if result.is_lossless else "FAIL")


if __name__ == "__main__":
    main()
