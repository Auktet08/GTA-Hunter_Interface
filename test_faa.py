from Bio import SeqIO
import textwrap
import re
import time

handle = "example_input/cb13b1a.gbff"

def line_org(feat, record_info, count):
    q = feat.qualifiers
    location = re.sub(r"[\[\]\(\)\+]", "", str(feat.location).replace(":",".."))
    string = (f">lcl|{record_info}_prot_{count} "
              f"[location={location}] "
              f"[locus_tag={q.get('locus_tag',['NULL'])[0]}] "
              f"[protein={q.get('product',['NULL'])[0]}] "
              f"[protein_id={q.get('protein_id',['NULL'])[0]}] ")
    return string

def per_input(og_file, destination):
    count = 0
    with open("placehold.txt", "w") as file:
        for record in SeqIO.parse(og_file, "gb"):
            cur_rec = record.id
            for feature in record.features:
                if feature.type == "CDS":
                    try:
                        string = str(feature.qualifiers.get("translation")[0])
                    except (TypeError, KeyError):
                        continue
                    count += 1
                    file.write(line_org(feature, cur_rec, count) + "\n")
                    for segment in textwrap.wrap(string):
                        file.write(segment + "\n")
                elif feature.type == "source":
                    genus, species = feature.qualifiers["organism"][0].split()[:2]
                    strain = feature.qualifiers["strain"][0]
                    name_file = f"{genus}_{species}_{strain}.faa"

per_input(handle)
