# - [x] Load the text input
# - [x] Load the HTML template
# - [x] Convert the text input into appropriate HTML with the proper tags
# - [x] Make sure that the script can also handle up to 4 kanji
# - [x] Combine the new HTML and the HTML template 
# - [x] Save the combined HTML as a new file
# - [x] Create a file choose prompt
# - [x] Use the dominate library
# - [x] Add example for markup
# - [x] Make Github repo

import os
from os.path import exists
import re
import sys
import dominate
from dominate.tags import *
from dominate.util import raw
from tkinter import filedialog
import argparse # for optional input arguments

# Create ArgumentParser object
parser = argparse.ArgumentParser(description='Select input file')
parser.add_argument('filepath', type = str, nargs = '?', default = 'choose')
args = parser.parse_args()
if args.filepath == 'choose':
    select_file_dialog = True
else:
    select_file_dialog = False

# ========== IMPORT THE FILES ===============
# load tkinter filedialog to display a dialog for the user to choose a file
# Let user choose a file
# Function to open a file in the system
def open_file():
    # print('Please choose a source file.')
    if select_file_dialog:
        fpath = filedialog.askopenfilename(title = "テキストファイルを選択してください", filetypes = (("text files", ["*.txt","*.md"]), ("all files", "*.*")))
        if fpath == '':
            sys.exit()
    else:
        fpath = args.filepath
    file = open(fpath,'r')
    input_file = file.readlines()
    dirname, fname = os.path.split(fpath)
    file.close()
    return (input_file, dirname, fname)

# Prompt the user to choose a text file
(raw_file, directory, filename) = open_file()

# =========== STRUCTURE THE INFORMATION

# Remove all new lines and all white additional white space from file
input_file = [line.strip() for line in raw_file]

# Remove all empty lines that are more than two in a row
input_file = [input_file[i] for i in range(len(input_file)) if not (input_file[i] == input_file[i-1] == '')]

# find metadata
metadata = {}
# find first empty line
l = input_file.index('') # until the next empty line

for line in input_file[:l]:
    (key, value) = line.split(': ')
    metadata[key] = value

# for type in ['gakunen', 'date']:
#     search_str = "(" + type + ": )(.*)"
#     r = re.compile(search_str)
#     newlist = list(filter(r.match, input_file))
#     metadata[type] = re.search(search_str, newlist[0]).group(2)

# Define HTML tags that should replace the brackets
cloze_tag = "<span class='cloze'>"
span_close_tag = "</span>"
box_tag = "<span class='box box2'></span>"
bracket_open_tag = "<ruby><span class='box'></span><rt>"
bracket_close_tag = "</rt></ruby>"
strong_open_tag = "<strong>"
strong_close_tag = "</strong>"
kanji_tag = "<span class = 'kanji'>" 

# Loop over all the tasks that are the file
blocks = {}
if any('task_1:' in line for line in input_file):
    task_1 = []
    blocks['task_1'] = task_1
if any('task_2:' in line for line in input_file):
    task_2 = []
    blocks['task_2'] = task_2
if any('answers:' in line for line in input_file):
    answers = []
    blocks['answers'] = answers

# for task in ['task_1', 'task_2', 'answers']:
for task in blocks:
    # find the beginning and end of each block
    a = input_file.index(task+':') # beginning line
    b = input_file[a:].index('') # until the next empty line
    # loop over all the relevant lines and add them to a list for each task
    offset = 1
    if task != 'answers':
        offset = 2
        _, instr = input_file[a+1].split(': ')
        if task == 'task_1':
            task_1_instr = instr
        else:
            task_2_instr = instr
    for item in input_file[a+offset:a+b]:
        (key, value) = item.split('. ')
        locals()[task].append(value)
        
# for-loop over all the task items of task 1 here
for i in range(len(task_1)):
    text = task_1[i]
    if ')' in text:
        # replace opening brackets in the middle of jukugo
        text = re.sub(r"\)\(", ")" + bracket_open_tag, text)
        # replace closing brackets in the middle of jukugo
        text = re.sub(r"\)<", bracket_close_tag + "<", text)
        # replace the remaining closing brackets
        text = re.sub(r"\)", bracket_close_tag + span_close_tag, text)
        # replace the remaining opening brackets
        text = re.sub(r"\(", cloze_tag + bracket_open_tag, text)
        # write to the task list
    if '）' in text:
        # replace opening brackets in the middle of jukugo
        text = re.sub(r"）（", "）" + bracket_open_tag, text)
        # replace closing brackets in the middle of jukugo
        text = re.sub(r"）<", bracket_close_tag + "<", text)
        # replace the remaining closing brackets
        text = re.sub(r"）", bracket_close_tag + span_close_tag, text)
        # replace the remaining opening brackets
        text = re.sub(r"（", cloze_tag + bracket_open_tag, text)
    # write to the task list
    task_1[i] = text
    
# for-loop over all the task items of task 2 here
for i in range(len(task_2)):
    text = task_2[i]
    # add the box to the beginning of the line
    text = cloze_tag + box_tag + span_close_tag + text
    if ')' in text:
        # replace opening square brackets with strong tag
        text = re.sub(r"\[", strong_open_tag, text)
        # replace closing square brackets with strong tag
        text = re.sub(r"\]", strong_close_tag, text)
        # replace opening parentheses with span kanji class tag
        text = re.sub(r"\(", kanji_tag, text)
        # replace closing parentheses with span tag
        text = re.sub(r"\)", span_close_tag, text)
    if '）' in text:
        # replace opening square brackets with strong tag
        text = re.sub(r"【", strong_open_tag, text)
        # replace closing square brackets with strong tag
        text = re.sub(r"】", strong_close_tag, text)
        # replace opening parentheses with span kanji class tag
        text = re.sub(r"（", kanji_tag, text)
        # replace closing parentheses with span tag
        text = re.sub(r"）", span_close_tag, text)
    # write to the task list
    task_2[i] = text

# =========== CREATE THE HTML =======================================
# =========== EMBED A VERSION OF THE CSS IN THE HTML ================
style_css = """
/* make the text vertical */
html {
    -webkit-writing-mode:   vertical-rl;
    -moz-writing-mode:      vertical-rl;
    -ms-writing-mode:       vertical-rl;
    writing-mode:           vertical-rl;
    text-orientation: upright;
    font-family: "UD Digi Kyokasho NK-R", "ヒラギノ角ゴ Pro W3", "Hiragino Kaku Gothic Pro",Osaka, "メイリオ", Meiryo, "ＭＳ Ｐゴシック", "MS PGothic", sans-serif;
}

/* p { */
/*     line-height: 1.5; */
/* } */
p.name {
    text-align: right;
}
p {
    line-height: 2;
}

/* style type for ordered list up to 5*/
@counter-style custom-ordered {
    system: cycle;
    symbols: '⑴' '⑵' '⑶' '⑷' '⑸' '⑹' '⑺' '⑻';
    suffix: ' ';
}

@counter-style katakana-custom {
    system: cycle;
    symbols: 'ア' 'イ' 'ウ' 'エ' 'オ';
    suffix: ' ';
}
ol {
    line-height: 2;
    list-style-type: custom-ordered;
}
ol.answers {
    list-style-type: katakana-custom !important;
    display: inline-block;
    border: 1px double grey;
    padding: 50px 10px 20px 10px;
    line-height: 1.2;
    margin-right: 5px;
}
ul.task {
    list-style-type: '■ ';
}

/* styling the cloze box */
span.box {
    display: inline-block;
    width: 3em;
    height: 3em;
    border: 1px double black;
    background-color: rgb(250, 250, 250);
    margin-left: 20px;
    margin-right: 20px;
    /* vertical-align: middle; */
    /* margin-left: 0.8em; */
}

span.cloze {
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    /* line-height: normal; */
}

span.box2 {
    width: 2em !important;
    height: 2em !important;
}

li > strong {
    font-size: 2em;
}

strong > span.kanji {
    /* font-size: 1.5em; */
    text-decoration: overline;
    line-height: 2;
}

/* styling the ruby over the text box */
rb, rt {
    /* display: inline; */
    /* line-height: 1; */
    margin-left: 10px;
    /* margin-right: 10px; */
    font-size: 0.7em;
}
ruby {
    /* display: inline-flex; */
    /* flex-direction: column-reverse; */
    /* text-align: center; */
    ruby-align: center;
}

/* split the paper in half */
.column {
    display: flex;
}
.row_top {
    flex: 50%;
    padding-bottom: 2em;
    border-bottom: 2px dashed black;
}
.row_bottom {
    padding-top: 2em;
    flex: 50%;
}
"""

doc = dominate.document(title = 'Kanji Test')
with doc.head:
    if os.path.exists('kanji_test.css'):
        link(rel='stylesheet', type='text/css', href='kanji_test.css', media='all')
    else: 
        style(raw(style_css))

with doc:
    with div():
        attr(cls='column')
        with div():
            attr(cls='row_top')
            h2('　　' + metadata['title'] + '　　' + metadata['gakunen'])
            with p(metadata['date'] + '　　' + '名前【　　　　　　　　　　　　　　　　　　　　】'):
                attr(cls='name')
            if 'task_1' in blocks:
                with ul():
                    attr(cls='task')
                    li(task_1_instr)
                with ol():
                    for item in task_1:
                        li(raw(item))
        if 'task_2' in blocks:
            with div():
                attr(cls='row_bottom')
                with ul():
                    attr(cls='task')
                    li(task_2_instr)
                with ol():
                    for item in task_2:
                        li(raw(item))
                if 'answers' in blocks:
                    with ol():
                        attr(cls='answers')
                        for item in answers:
                            li(item)

# ================ EXPORT THE HTML =====================
output_filename = filename.split(".")[0] + ".html"
full_output_path = os.path.join(directory, output_filename)

if select_file_dialog:
# ================ Ask for filename before export ==========
    f = filedialog.asksaveasfile(mode = 'w', confirmoverwrite = True, defaultextension = '.html', filetypes = [("HTML", "*.html")], initialfile = output_filename)
    if f == '':
        sys.exit()
else:
    if os.path.exists(full_output_path):
        print("A file with the name", str(full_output_path), "already exists in the chosen directory.\nIf you continue, it will be overwritten.")
        user_input = input("Do you want to continue? (Y/n)")
        if user_input not in ['y', 'Y', 'yes', 'Yes']:
            sys.exit() # terminate the script
    f = open(full_output_path, 'w')

print(doc, file = f)
f.close()

if not select_file_dialog:
    print('Kanji test has been successfully created at ' + full_output_path)