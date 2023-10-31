from html.entities import name2codepoint
from html.parser import HTMLParser
from zipfile import ZipFile
from math import ceil, log
import argparse
import shutil
import string
import re
import os


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global data_html
        attributes = []

        for attr in attrs:
            attributes.append(attr)

        data_html.append((("Start tag:", tag), ("attr:", attributes)))

    def handle_endtag(self, tag):
        global data_html

        data_html.append(("End tag:", tag))

    def handle_data(self, data):
        global data_html

        data_html.append(("Data:", data))


def bolding(text):
    parts = re.findall(r"[^\s]+", text)
    new_text = ""

    for part in parts:
        if part in string.punctuation or part in string.digits:
            new_text += " " + part
        else:
            if len(part) <= 3:
                new_part = ""
                new_part = f"<b>{part[0]}</b>"
                new_part += "".join(part[1:])
                new_text += " " + new_part
            else:
                point = ceil(log(len(part), 2))
                new_part = ""
                new_part = f"<b>{part[0:point]}</b>"
                new_part += "".join(part[point:])
                new_text += " " + new_part

    return new_text


parser = argparse.ArgumentParser()

parser.add_argument("epubfile", help="put a path to your epub file in here")

file_path = parser.parse_args().epubfile
file_name = os.path.basename(file_path)
epub_path = os.getcwd() + "/hayai_" + file_name
unzip_path = os.getcwd() + "/" + (file_name + "_zip/")


try:
    with ZipFile(file_path, "r") as zipObj:
        zipObj.extractall(unzip_path)
except:
    with ZipFile(os.getcwd() + "/" + file_path, "r") as zipObj:
        zipObj.extractall(unzip_path)


first_tags = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN' 'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>\n"""
htmls = []

# r = root, d = directories, f = files
for r, d, f in os.walk(unzip_path):
    for hfile in f:
        if hfile[-4:] == "html":
            htmls.append(os.path.join(r, hfile))
        elif hfile[-3:] == "htm":
            htmls.append(os.path.join(r, hfile))


for html in htmls:
    with open(html, "r", encoding="utf-8") as f:
        html_data = f.read()

    data_html = []
    parser = MyHTMLParser()

    parser.feed(html_data)

    full_html = ""

    for html_part in data_html:
        if html_part[0] == "Data:":
            # full_html += html_part[1]
            # full_html += f"<b>{html_part[1]}</b>"
            full_html += bolding(html_part[1])

        if len(html_part) == 2 and html_part[0][0] == "Start tag:":
            tag = "<" + html_part[0][1]
            full_attr = []

            for attr in html_part[1][1]:
                full_attr.append(attr[0] + f'="{attr[1]}"')

            full_attr = " ".join(full_attr)

            if not full_attr:
                tag += full_attr + ">"
            else:
                tag += " " + full_attr + ">"

            full_html += tag

        if html_part[0] == "End tag:":
            tag = f"</{html_part[1]}>\n"
            full_html += tag

    full_html = first_tags + full_html

    with open(html, "w", encoding="utf-8") as f:
        f.write(full_html)


os.chdir(unzip_path)
shutil.make_archive(epub_path, "zip", "./")

try:
    os.remove((epub_path + ".zip")[:-4])
except:
    pass

os.rename((epub_path + ".zip"), (epub_path + ".zip")[:-4])
