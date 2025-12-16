import sys
import os
import struct



def lzw_compress_data(uncompressed_bytes):
    # Initialize dictionary with standard ASCII (0-255)
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}

    w = b""
    compressed_data = []

    # Iterate through every byte in the input
    for byte_val in uncompressed_bytes:
        c = bytes([byte_val])
        wc = w + c

        if wc in dictionary:
            w = wc
        else:
            # Output the code for the known pattern w
            compressed_data.append(dictionary[w])

            if dict_size < 65536:
                dictionary[wc] = dict_size
                dict_size += 1

            w = c

    if w:
        compressed_data.append(dictionary[w])

    return compressed_data


def lzw_decompress_data(compressed_codes):
    # Initialize dictionary with standard ASCII
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    if not compressed_codes:
        return b""

    # Use bytearray for efficient mutable byte concatenation
    result = bytearray()

    w_code = compressed_codes[0]
    w = dictionary[w_code]
    result.extend(w)

    for k in compressed_codes[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0:1]
        else:
            raise ValueError(f"Bad compressed code: {k}")

        result.extend(entry)

        if dict_size < 65536:
            dictionary[dict_size] = w + entry[0:1]
            dict_size += 1

        w = entry

    return bytes(result)

def compress_file(input_file, output_file):
    try:
        print(f"Reading {input_file}...")
        with open(input_file, 'rb') as f_in:
            data = f_in.read()

        print("Running LZW compression...")
        compressed_codes = lzw_compress_data(data)

        print(f"Writing to {output_file}...")
        with open(output_file, 'wb') as f_out:
            for code in compressed_codes:
                f_out.write(struct.pack('>H', code))

        original_size = len(data)
        compressed_size = os.path.getsize(output_file)
        ratio = (compressed_size / original_size) * 100

        print(f"Successfully compressed '{input_file}' to '{output_file}'")
        print(f"Original: {original_size} bytes | Compressed: {compressed_size} bytes | Ratio: {ratio:.2f}%")

    except Exception as e:
        print(f"Error during compression: {e}")
        sys.exit(1)

def decompress_file(input_file, output_file):
    try:
        print(f"Reading {input_file}...")
        compressed_codes = []

        # 1. Read Binary Input (2 bytes at a time)
        with open(input_file, 'rb') as f_in:
            while True:
                chunk = f_in.read(2)
                if not chunk:
                    break
                # Unpack 2 bytes back into an integer
                code = struct.unpack('>H', chunk)[0]
                compressed_codes.append(code)

        # 2. Run LZW Decompression
        print("Running LZW decompression...")
        data = lzw_decompress_data(compressed_codes)

        # 3. Write Output
        print(f"Writing to {output_file}...")
        with open(output_file, 'wb') as f_out:
            f_out.write(data)

        print(f"Successfully decompressed '{input_file}' to '{output_file}'")

    except Exception as e:
        print(f"Error during decompression: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("  Compress:   python stock_compress.py c <input.csv> <output.dat>")
        print("  Decompress: python stock_compress.py -d <input.dat> <output.csv>")
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    # Handle 'c' or '-c' for compression
    if mode in ['c', '-c']:
        compress_file(input_file, output_file)
    # Handle 'd' or '-d' for decompression
    elif mode in ['d', '-d']:
        decompress_file(input_file, output_file)
    else:
        print(f"Error: Unknown mode '{mode}'. Use 'c' for compress or '-d' for decompress.")
        sys.exit(1)


if __name__ == "__main__":
    main()