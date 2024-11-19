from pathlib import Path
import re
import csv

def main():
    timecode = "2024-11-19_164958"
    directory = Path(f"{timecode}_full_stacker")
    master_file = directory/f"{timecode}_master1.csv"

    out_parse(directory, master_file)

"""
out_parse
parse input directory and adds to master_log csv

"""

def out_parse(directory, master_file):
    # creates master_log csv
    with open(master_file, "w") as output_csv:
        # write header
        csv_writer = csv.DictWriter(output_csv, extrasaction="ignore",
            fieldnames = ['name', 'strain',
                          'location', 'genome', 'locus_tag', 'protein_id', 'protein', 'count',
                          'score', 'classification', 'gta_gene', "coding"])
        csv_writer.writeheader()
        # finds all output files to parse
        for result in directory.glob("*.out"):
            # parse file info and add to master_log
            files_info = csv_convert(result)
            csv_writer.writerows(files_info)

    # prints all information for visual
    print("\n === OUTPUT ===")
    print(directory)
    print(f" * {master_file.name}")
    for result in directory.glob("*.out"):
        print(f" +-- {result.name}")

def csv_convert(input_file):
    print(f"\n === FILE PARSE : {input_file.stem} ===")

    lcl_pattern = r"lcl\|([\w._]+)_prot.*_(\d+) "
    num_pattern = r"\](-?[\d.]+) +(\w+) +(\w+)"
    bracket_pattern = r" \[([\w_]+)=([^\]]+)\]"

    # determine actual filename from results_filename
    og_filename = str(input_file.stem).replace("results_", "")

    # pull name + strain from filename
    try:
        genus, species, strain = og_filename.split("_")
        name = f"{genus}_{species}"
    except ValueError:
        name = ""
        strain = og_filename

    all_rows = []
    # checks the results file
    with open(str(input_file), "r") as input_txt:
        # parse each line using pattern
        # add to "all_rows"
        for line in input_txt:
            # check if line contains searchable information
            if not re.search(r"\[", line):
                continue
            row_info = {}
            row_info["name"] = name
            row_info["strain"] = strain
            # pull from >lcl section
            if homologue_match := re.search(lcl_pattern, line):
                row_info["genome"] = homologue_match.group(1)
                row_info["count"] = homologue_match.group(2)
            # pull from all bracked information
            brackets = re.findall(bracket_pattern, line)
            for info in brackets:
                row_info[info[0]] = info[1]
            # parse information created by GTA Hunter
            if gta_scores := re.search(num_pattern, line):
                row_info["score"] = gta_scores.group(1)
                row_info["classification"] = gta_scores.group(2)
                row_info["gta_gene"] = gta_scores.group(3)

                # only if gta is found
                # search to find associated sequence information and pull coding region
                hom_num = row_info["gta_gene"]
                try:
                    seq_file = input_file.parent / og_filename / f"gta_homolog_{hom_num}_{og_filename}.faa"
                    with seq_file.open() as f:
                        string = ""
                        for line in f:
                            string += f.readline()
                        coding = string.replace("\n", "")
                        row_info["coding"] = coding
                except Exception:
                    pass
            all_rows.append(row_info)
        for row in all_rows:
            print(row)
    return all_rows
if __name__ == '__main__':
    main()