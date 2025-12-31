import pandas as pd
import os

def excel_to_compressed_format(excel_file):
    """
    Convert Excel to formats that are GUARANTEED to be smaller
    """
    df = pd.read_excel(excel_file)
    
    excel_size = os.path.getsize(excel_file)
    print(f"Excel size: {excel_size/1024/1024:.2f} MB")
    print("\nTesting different formats...")
    
    results = []
    
    # 1. Parquet (Columnar format - usually smallest)
    parquet_file = excel_file.replace('.xlsx', '.parquet')
    df.to_parquet(parquet_file, compression='gzip')
    parquet_size = os.path.getsize(parquet_file)
    results.append(('Parquet (gzip)', parquet_size, parquet_size/excel_size))
    
    # 2. Feather (Fast, good compression)
    feather_file = excel_file.replace('.xlsx', '.feather')
    df.to_feather(feather_file, compression='zstd')
    feather_size = os.path.getsize(feather_file)
    results.append(('Feather (zstd)', feather_size, feather_size/excel_size))
    
    # 3. Pickle with compression
    pickle_file = excel_file.replace('.xlsx', '.pkl.gz')
    df.to_pickle(pickle_file, compression='gzip')
    pickle_size = os.path.getsize(pickle_file)
    results.append(('Pickle (gzip)', pickle_size, pickle_size/excel_size))
    
    # 4. CSV with GZIP
    csv_gz_file = excel_file.replace('.xlsx', '.csv.gz')
    df.to_csv(csv_gz_file, index=False, compression='gzip')
    csv_gz_size = os.path.getsize(csv_gz_file)
    results.append(('CSV (gzip)', csv_gz_size, csv_gz_size/excel_size))
    
    # 5. HDF5
    hdf_file = excel_file.replace('.xlsx', '.h5')
    df.to_hdf(hdf_file, key='data', mode='w', complevel=9)
    hdf_size = os.path.getsize(hdf_file)
    results.append(('HDF5', hdf_size, hdf_size/excel_size))
    
    print("\n" + "="*60)
    print("FORMAT COMPARISON (Smaller is Better)")
    print("="*60)
    
    # Sort by size (smallest first)
    results.sort(key=lambda x: x[1])
    
    for name, size, ratio in results:
        size_mb = size/1024/1024
        status = "✓ SMALLER" if ratio < 1 else "⚠ LARGER"
        print(f"{name:15} {size_mb:6.2f} MB ({ratio:.2f}x) {status}")
    
    # Clean up temporary files
    for file in [parquet_file, feather_file, pickle_file, csv_gz_file, hdf_file]:
        if os.path.exists(file):
            os.remove(file)
    
    return results[0][0]  # Return name of smallest format

# Usage
if __name__ == "__main__":
    best_format = excel_to_compressed_format(r'F:\My Own Thing\VST Dashboard.xlsx')
    print(f"\nRecommended format: {best_format}")