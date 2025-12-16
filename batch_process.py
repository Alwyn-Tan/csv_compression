import os
import glob
import subprocess
import pandas as pd
import time
import sys
import pandas
import openpyxl

INPUT_FOLDER = 'stocks'
COMPRESSED_FOLDER = 'compressed'
DECOMPRESSED_FOLDER = 'decompressed'
OUTPUT_XLSX = 'stock_compress.xlsx'
COMPRESSOR_SCRIPT = 'stock_compress.py'

def run_batch_processing():
    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Folder '{INPUT_FOLDER}' not found.")
        print("Please unzip 'stocks.zip' into a folder named 'stocks' in this directory.")
        return

    os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
    os.makedirs(DECOMPRESSED_FOLDER, exist_ok=True)

    csv_files = glob.glob(os.path.join(INPUT_FOLDER, '*.csv'))
    if not csv_files:
        print(f"No .csv files found in '{INPUT_FOLDER}'.")
        return

    print(f"Found {len(csv_files)} CSV files. Starting batch compression...")
    print(f"Compressed output -> '{COMPRESSED_FOLDER}/'")
    print(f"Decompressed output -> '{DECOMPRESSED_FOLDER}/'")
    print("-" * 60)

    results = []
    start_time = time.time()

    #Loop through all CSV files
    for i, csv_path in enumerate(csv_files):
        filename = os.path.basename(csv_path)
        base_name = os.path.splitext(filename)[0]  # e.g., "AAPL"

        dat_path = os.path.join(COMPRESSED_FOLDER, base_name + '.dat')
        restored_csv_path = os.path.join(DECOMPRESSED_FOLDER, filename)

        try:
            #Compression
            cmd_compress = [sys.executable, COMPRESSOR_SCRIPT, 'c', csv_path, dat_path]
            subprocess.run(cmd_compress, check=True, capture_output=True)

            #Decompression
            cmd_decompress = [sys.executable, COMPRESSOR_SCRIPT, '-d', dat_path, restored_csv_path]
            subprocess.run(cmd_decompress, check=True, capture_output=True)

            #Metrics
            if os.path.exists(dat_path):
                original_size = os.path.getsize(csv_path)
                compressed_size = os.path.getsize(dat_path)

                ratio = (compressed_size / original_size) if original_size > 0 else 0

                results.append({
                    'File Name': filename,
                    'Original Size (Bytes)': original_size,
                    'Compressed Size (Bytes)': compressed_size,
                    'Compression Ratio': ratio
                })
            else:
                print(f"[!] Warning: Failed to generate {dat_path}")

        except subprocess.CalledProcessError as e:
            print(f"[!] Error processing {filename}: {e}")

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(csv_files)} files...")

        if results:
            df = pd.DataFrame(results)
            df['Compression Ratio %'] = df['Compression Ratio'].map('{:.2%}'.format)

            total_orig = df['Original Size (Bytes)'].sum()
            total_comp = df['Compressed Size (Bytes)'].sum()
            total_saving = (1 - (total_comp / total_orig)) * 100

            print(f"Batch Processing Complete in {time.time() - start_time:.2f} seconds")
            print(f"Total Files: {len(df)}")
            print(f"Total Original Size:   {total_orig / (1024 * 1024):.2f} MB")
            print(f"Total Compressed Size: {total_comp / (1024 * 1024):.2f} MB")
            print(f"Overall Space Saving:  {total_saving:.2f}%")

            df.to_excel(OUTPUT_XLSX, index=False)
            print(f"Report saved to '{OUTPUT_XLSX}'")

if __name__ == "__main__":
    run_batch_processing()