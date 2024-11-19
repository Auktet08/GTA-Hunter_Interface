from pathlib import Path
import subprocess
from datetime import datetime
from opening_og import out_parse
import sys
import shutil
from prepare_input import faa_convert


def main():
    input_folder_name = "faa_testing_start"
    output_folder_name = "gbff_success"
    gta_hunter = "GTA_Hunter.py"
    gta_hunter_location = "/Users/northk/Documents/gozzi/GTA-Hunter-v1/"

    master_folder_name = "master"

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

    # store genome names
    confirm_input(input_folder, output_path)

    """
    === Create Folders ===
    """

    # create output folder
    output_path.mkdir()

    # create modified input folder
    new_input_folder = output_path / "input"
    new_input_folder.mkdir()

    faa_convert(input_folder, new_input_folder)

    input_folder = new_input_folder

    # ensure genome list is set properly.
    # genome list must be formatted correctly!

    # prepare_input(input_folder)
    genome_list = ""

    # create folder for each genome
    # for genome in genome_list:
    #     new_temp_folder = output_path/genome
    #     new_temp_folder.mkdir()

    for faa_file in input_folder.glob("*.faa"):
        # creates and names temp folder
        new_temp_folder = output_path/faa_file.stem
        new_temp_folder.mkdir()

    """
    === Run the Program ===
    """
    master_command = f"python {gta_hunter} -b -f {input_folder.resolve()} -o {output_path.resolve()} -O"
    # print(master_command)
    subprocess.run(f"cd {gta_hunter_location} && {master_command}", shell=True)

    """
    === Modify Output ===
    """

    # for each genome name
    for faa_file in input_folder.glob("*.faa"):
        # access associated temp path
        temp_path = output_path/faa_file.stem
        for file in output_path.glob("*.*"):
            # place into temp path
            if faa_file.stem in str(file) and str(file.stem).startswith("results") is False:
                file.replace(temp_path / file.name)

    """
    === Fix with CSV ===
    """
    master_file = output_path/f"{timecode}_master.csv"

    out_parse(output_path, master_file)

    # creates copy inside the master folder to optimize access
    shutil.copy(master_file, master_path / master_file.name)

def confirm_input(input_folder, output_path):
    all_filenames = []
    print("\n === INITIALIZE === ")
    print(f"All Files Detected in '{input_folder}' :")
    for file in input_folder.glob("*.[faa gbff gbk]*"):
        # update_filename = str(file.stem).replace(" ", "_")
        # if file.stem != update_filename:
        #     file.rename(Path(file.parent, update_filename + file.suffix))
        # all_filenames.append(update_filename)
        # print(f" +-- {update_filename}{file.suffix}")
        print(f" +-- {file.name}")
    print("\nOutput Folder:", output_path)
    
    # check to proceed
    proceed = input("\nPROCEED? [Y/N]: ")
    if proceed.casefold() == "n":
        sys.exit("sorry")

    # used for figuring out names of species
    return all_filenames

if __name__ == '__main__':
    main()