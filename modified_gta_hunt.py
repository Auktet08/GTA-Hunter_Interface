from pathlib import Path
import subprocess
from datetime import datetime
from opening_og import out_parse
import sys
import shutil
from prepare_input import faa_convert


def main():
    input_folder_name = "OneDrive_1_11-3-2024 2"
    output_folder_name = "full_stacker"
    gta_hunter = "GTA_Hunter.py"
    gta_hunter_location = "/Users/northk/Documents/gozzi/GTA-Hunter-v1/"

    master_folder_name = "master_log"

    """
    === Initialize ===
    """
    # initialize folder information (argparse)
    timecode = str(datetime.today().strftime('%Y-%m-%d_%H%M%S'))

    # set folder
    input_folder = Path(input_folder_name)
    output_path = Path(".")/f"{timecode}_{output_folder_name}"
    master_path = Path(master_folder_name)

    """
    === Parse Input ===
    """

    # check if all the inputs look correct
    confirm_input(input_folder, output_path)

    """
    === Create Folders ===
    """

    # create output folder
    output_path.mkdir()

    # create input folder for our converted .faa files
    new_input_folder = output_path / "input"
    new_input_folder.mkdir()

    # convert everything into .faa and place into new input folder
    faa_convert(input_folder, new_input_folder)

    input_folder = new_input_folder

    # creates subdir for each of our faa files
    for faa_file in input_folder.glob("*.faa"):
        # creates and names temp folder
        new_temp_folder = output_path/faa_file.stem
        new_temp_folder.mkdir()

    """
    === Run the Program ===
    """

    master_command = f"python {gta_hunter} -b -f {input_folder.resolve()} -o {output_path.resolve()} -O"
    # runs the master_log command
    subprocess.run(f"cd {gta_hunter_location} && {master_command}", shell=True)

    """
    === Modify Output ===
    """

    # for each genome name
    for faa_file in input_folder.glob("*.faa"):
        # access associated temp path
        temp_path = output_path/faa_file.stem
        for file in output_path.glob("*.*"):
            # redirects every printed file
            if faa_file.stem in str(file) and str(file.stem).startswith("results") is False:
                file.replace(temp_path / file.name)

    """
    === Fix with CSV ===
    """

    # creates master_log file csv
    master_file = output_path/f"{timecode}_master.csv"

    # parses every results to place into master_log file
    out_parse(output_path, master_file)

    # creates copy inside the master_log folder to optimize access
    shutil.copy(master_file, master_path / master_file.name)

"""
confirm_input
- displays all accessible folders
- prompts input to confirm and run
"""
def confirm_input(input_folder, output_path):
    all_filenames = []
    print("\n === INITIALIZE === ")
    print(f"All Files Detected in '{input_folder}' :")
    for file in input_folder.glob("*.[faa gbff gbk]*"):
        print(f" +-- {file.name}")
    print("\nOutput Folder:", output_path)
    
    # check to proceed
    print("\n** WARNING: For optimal results, .gbk and .faa filenames should be formated as 'genus_species_strain.ext'")
    proceed = input("\nPROCEED? [Y/N]: ")
    if proceed.casefold() == "n":
        sys.exit("sorry")

    # used for figuring out names of species
    return all_filenames

if __name__ == '__main__':
    main()