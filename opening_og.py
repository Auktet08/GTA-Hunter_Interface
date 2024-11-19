from pathlib import Path
import re
import csv

def main():
    timecode = "2024-11-12_191218"
    directory = Path(f"{timecode}_gbff_success")
    master_file = directory/f"{timecode}_master.csv"

    out_parse(directory, master_file)

def out_parse(directory, master_file):
    with open(master_file, "w") as output_csv:
        # write header
        csv_writer = csv.DictWriter(output_csv, extrasaction="ignore",
            fieldnames = ['name', 'strain',
                          'location', 'genome', 'locus_tag', 'protein_id', 'protein', 'count',
                          'score', 'classification', 'gta_gene', "coding"])
        csv_writer.writeheader()
        for result in directory.glob("*.out"):
            files_info = csv_convert(result)
            csv_writer.writerows(files_info)
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

    # pull name + strain from filename
    _, genus, species, strain = str(input_file.stem).split("_")
    name = f"{genus}_{species}"

    all_rows = []
    with open(str(input_file), "r") as input_txt:
        # parse each line
        for line in input_txt:
            if not re.search(r"\[", line):
                continue
            row_info = {}
            row_info["name"] = name
            row_info["strain"] = strain
            if homologue_match := re.search(lcl_pattern, line):
                row_info["genome"] = homologue_match.group(1)
                row_info["count"] = homologue_match.group(2)
            brackets = re.findall(bracket_pattern, line)
            for info in brackets:
                row_info[info[0]] = info[1]
            if gta_scores := re.search(num_pattern, line):
                row_info["score"] = gta_scores.group(1)
                row_info["classification"] = gta_scores.group(2)
                row_info["gta_gene"] = gta_scores.group(3)

                # pull sequence information
                hom_num = row_info["gta_gene"]
                try:
                    seq_file = input_file.parent / f"{name}_{strain}" / f"gta_homolog_{hom_num}_{name}_{strain}.faa"
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