from pathlib import Path
import subprocess
from datetime import datetime
import argparse
import sys
import shutil
from prepare_input import faa_convert
from opening_og import out_parse

# file name of the actual GTA Hunter
GTA_HUNTER = "GTA_Hunter.py"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_folder",
        type=str, nargs=1,
        help="input folder containing .gbff .gbk or .faa files"
    )
    parser.add_argument(
        "-o", "--output",
        type=str, nargs=1,
        help="specific name for output file"
    )
    parser.add_argument(
        "-g", "--gta_hunter",
        type=str, nargs=1,
        help="absolute path to the GTA-Hunter Folder"
    )

    args = parser.parse_args()

    if args.input_folder is not None:
        input_folder_name = args.input_folder[0]
    else:
        input_folder_name = input("INPUT FOLDER NAME: ")

    if args.gta_hunter is not None:
        gta_hunter_location = args.gta_hunter[0]
    else:
        with open("settings.txt", "r+") as settings:
            content = settings.readlines()
            try:
                gta_hunter_location = content[1]
            except IndexError:
                print("INITIALIZING...")
                gta_hunter_location = input("ABSOLUTE PATH OF GTA HUNTER FOLDER: ")
                settings.write(f"\n{gta_hunter_location}")

    if args.output is not None:
        output_folder_name = args.output[0]
    else:
        output_folder_name = "output"

    """
    === Initialize ===
    """
    # initialize folder information (argparse)
    timecode = str(datetime.today().strftime('%Y-%m-%d_%H%M%S'))

    # set folder
    input_folder = Path(input_folder_name)
    output_path = Path(".")/f"{timecode}_{output_folder_name}"
    master_path = Path("master_log")

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

    master_command = f"python {GTA_HUNTER} -b -f {input_folder.resolve()} -o {output_path.resolve()} -O"
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

    # parses every result to place into master_log file
    out_parse(output_path, master_file)

    # creates copy inside the master_log folder to optimize access
    shutil.copy(master_file, master_path / master_file.name)

    print(f"\nDone.\n")

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
        sys.exit("sorry\n")

    # used for figuring out names of species
    return all_filenames

if __name__ == '__main__':
    main()