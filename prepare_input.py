import shutil
from pathlib import Path
import re
from Bio import SeqIO
import textwrap

def main():
    # initialize testing
    input_directory = Path("gbff_test")
    new_input_dir = Path("faa_test_end")

    # faa_convert for input directory
    faa_convert(input_directory, new_input_dir)

"""
faa_convert
input_folder(gbff, gbk, faa) -> output_folder(faa)
1. ensures that filenames are correct
- gbff : pulls from 
- gbk, faa : user input / confirmation [file_renamer]
2. gbff -> faa -> destination / faa [per_input]
3. gbk -> destination / faa [per_input]
4. faa -> destination / faa
"""
def faa_convert(source, destination):
    print(f"\nINPUT: {destination}")
    for file in source.glob("*.*"):
        if file.suffix == ".gbff":
            print(per_input(file, destination))
        elif file.suffix == ".gbk":
            print(per_input(file, destination))
        elif file.suffix == ".faa":
            # make sure name information is correct!
            shutil.move(file, destination / file.name)
            print(f"+-- {file.name}")

"""
per_input
gbff -> faa -> destination
1. for each feature in file : 
- a. parse information
- b. convert into line in faa inside workspace 
"""
def per_input(og_file, destination):
    count = 0
    # creates temp workspace
    with open("placehold.txt", "w") as file:
        for record in SeqIO.parse(og_file, "gb"):
            cur_rec = record.id
            # runs for every feature
            for feature in record.features:
                if feature.type == "CDS":
                    try:
                        string = str(feature.qualifiers.get("translation")[0])
                    except (TypeError, KeyError):
                        continue
                    count += 1
                    # write file header
                    file.write(line_org(feature, cur_rec, count) + "\n")
                    # include coding region as block of text
                    for segment in textwrap.wrap(string):
                        file.write(segment + "\n")
                # determine file name
                elif feature.type == "source":
                    try:
                        # determine name info from internal
                        genus, species = feature.qualifiers["organism"][0].split()[:2]
                        strain = str(feature.qualifiers["strain"][0])
                        strain.replace(" ", "-")
                        name_file = (f"{genus}_{species}_{strain}").replace(".","")
                    except (TypeError, KeyError):
                        # if fail, filename matches actual file name
                        name_file = og_file.stem

    if count == 0:
        return f"ERROR: {og_file}"
    new_file = destination / name_file
    shutil.move("placehold.txt", new_file.with_suffix(".faa"))
    return f"+-- {new_file.name}"

def line_org(feat, record_info, count):
    q = feat.qualifiers
    location = re.sub(r"[\[\]\(\)\+]", "", str(feat.location).replace(":",".."))
    string = (f">lcl|{record_info}_prot_{q.get('protein_id',['NULL'])[0]}_{count} "
              f"[location={location}] "
              f"[locus_tag={q.get('locus_tag',['NULL'])[0]}] "
              f"[protein={q.get('product',['NULL'])[0]}] "
              f"[protein_id={q.get('protein_id',['NULL'])[0]}] ")
    return string

if __name__ == '__main__':
    main()