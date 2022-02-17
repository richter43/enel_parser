import csv
import re

from localparser import parse
import pdfplumber
from typing import List, Dict


fieldnames = ["num_conto", "data", "costo_totale", "costo_energia", "costo_oneri", "costo_trasporto", "costo_iva_imposte", "costo_tv", "costo_ricalcoli", "kwh_lettura", "kwh_fatturato"]

def save_csv(args, vals_dict: List[Dict[str,str]]):
    with open(args.output_file, 'w') as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in vals_dict:
            writer.writerow(line)

def checks_firstpage(text: str, values: Dict[str,str]) -> str:
    # Client number
    tmp = text.split()
    if "300" in tmp:
        values["num_conto"] = "-".join(tmp[0:3])
    # Total cost
    if "elettrica" in tmp and len(tmp) > 3:
        if "," in tmp[3]:
            values["costo_totale"] = tmp[3]
    if "Del" in tmp:
        values["data"] = tmp[1]
    if "Spesa" in tmp:
        if "l'energia" in tmp:
            idx = tmp.index("l'energia")
            values["costo_energia"] = tmp[idx+1].split("_")[0]
        if "oneri" in tmp:
            idx = tmp.index("oneri")
            values["costo_oneri"] = tmp[idx+2].split("_")[0]
        if "il" in tmp:
            idx = tmp.index("il")
            values["costo_trasporto"] = tmp[idx+1].split("_")[0]
    if "IVA" in tmp:
        idx = tmp.index("IVA")
        if "," in tmp[idx + 1]:
            values["costo_iva_imposte"] = tmp[idx+1].split("_")[0]
    if "privato" in tmp:
        tmp_idx = -1
        for idx, i in enumerate(tmp):
            if "VF" in i:
                tmp_idx = idx
                break
        if "," in tmp[tmp_idx+1]:
            values["costo_tv"] = tmp[tmp_idx+1]
    if "Ricalcoli" in tmp and "Spesa" not in tmp:
        values["costo_ricalcoli"] = tmp[2].split("_")[0]


def clean_trailing_dots(string: str) -> str:
    pattern = "^\.+"
    return re.sub(pattern, "", string)


def checks_secondpage(text: str, values: Dict[str,str]) -> str:
    tmp = text.split()
    if "attiva" in tmp and "kWh" in tmp:
        attiva_list = text.split("attiva")
        values["kwh_lettura"] = clean_trailing_dots(attiva_list[-2].split()[-1])
        values["kwh_fatturato"] = clean_trailing_dots(attiva_list[-1].split()[2])
    pass

def extract_info(text_list: List[str], function, dict_pages: Dict[str,str]) -> str:

    for i in text_list:
        function(i, dict_pages)

    return dict_pages


def print_present(text_list, text):
    for i in text_list:
        if text in i:
            print(i.split())

def handle_pdf(filename:str):
    values = {}
    with pdfplumber.open(filename) as pdf:
        page = pdf.pages[0]
        text = page.extract_text(layout=True)
        text_list = text.split("\n")

        extract_info(text_list, checks_firstpage, values)

        page = pdf.pages[1]
        text = page.extract_text(layout=True)
        text_list = text.split("\n")
        # print_present(text_list, "kWh")
        extract_info(text_list, checks_secondpage, values)

    return values

def main():

    args = parse()

    with open(args.filename, "r") as f:
        first_page_list = []
        for filename in f.readlines():
            values = handle_pdf(filename.split("\n")[0])
            first_page_list.append(values)

    save_csv(args, first_page_list)


if __name__ == "__main__":
    main()




