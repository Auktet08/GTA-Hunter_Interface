from pathlib import Path
from datetime import datetime
import shutil

def main():

    # set folder of interest
    downloaded_ncbi = Path("ncbi_dataset (1)")
    timecode = str(datetime.today().strftime('%Y-%m-%d_%H%M%S'))
    collected_gbff = Path(f"{timecode}_input_gbff")

    ncbi_db_extract(downloaded_ncbi, collected_gbff)

def ncbi_db_extract(ncbi_dir_name, collected_gbff):
    collected_gbff.mkdir()
    print(f"\nNCBI Database: {ncbi_dir_name}")
    print(f"ALL .GBFF MOVED TO: {collected_gbff}\n")
    count = 0
    for directory in Path(ncbi_dir_name/"ncbi_dataset/data").iterdir():
        if directory.is_dir():
            count += 1
            rename_file(directory, collected_gbff)
    print(f"{count} genomic.gbff processed\n")

def rename_file(start_dir, end_dir):
    gbff_file = start_dir/"genomic.gbff"
    new_file = end_dir/start_dir.stem
    shutil.move(gbff_file, new_file.with_suffix(".gbff"))

if __name__ == '__main__':
    main()