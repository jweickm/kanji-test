# - [x] Load the text input
# - [x] Load the HTML template
# - [x] Convert the text input into appropriate HTML with the proper tags
# - [x] Make sure that the script can also handle up to 4 kanji
# - [x] Combine the new HTML and the HTML template 
# - [x] Save the combined HTML as a new file
# - [x] Create a file choose prompt
# - [x] Use the dominate library
# - [ ] Add example for markup
# - [ ] Make Github repo

import os
import re
from unittest import TextTestResult
import dominate
from dominate.tags import *
from dominate.util import raw
import tkinter
from tkinter import filedialog

DEBUG = False

if DEBUG:
    with open ('template.txt') as file:
        input_file = file.readlines()
    file.close()
else:
# ========== IMPORT THE FILES ===============
# load tkinter filedialog to display a dialog for the user to choose a file
# Let user choose a file
# Function to open a file in the system
    def open_file():
        print('Please choose a source file.')
        filepath = filedialog.askopenfilename(title = "テキストファイルを選択してください", filetypes = (("text files", "*.txt"), ("all files", "*.*")))
        file = open(filepath,'r')
        input_file = file.readlines()
        filename = filepath.split('/')[-1]
        file.close()
        return (input_file, filename)

# Prompt the user to choose a text file
    (input_file, filename) = open_file()

# =========== STRUCTURE THE INFORMATION

len(input_file)
# Remove all new lines from file
input_file = [line.replace('\n', '') for line in input_file]

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
box_tag = "<span class='box'></span>"
bracket_open_tag = "<ruby><span class='box'></span><rt>"
bracket_close_tag = "</rt></ruby>"
strong_open_tag = "<strong>"
strong_close_tag = "</strong>"
kanji_tag = "<span class = 'kanji'>" 

# Loop over all the tasks
task_1 = []
task_2 = []
answers = []
blocks = {'task_1': task_1, 'task_2': task_2, 'answers': answers}

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

# =========== CREATE THE HTML ===============

doc = dominate.document(title = 'Kanji Test')
with doc.head:
    link(rel='stylesheet', type='text/css', href='kanji_test.css', media='all')

with doc:
    with div():
        attr(cls='column')
        with div():
            attr(cls='row_top')
            p(metadata['title'] +'　' + metadata['gakunen'] + '　' + metadata['date'])
            with p('名前【　　　　　　　　　　　　　　　　　　　　】'):
                attr(cls='name')
            with ul():
                attr(cls='task')
                li(task_1_instr)
            with ol():
                for item in task_1:
                    li(raw(item))
        with div():
            attr(cls='row_bottom')
            with ul():
                li(task_2_instr)
            with ol():
                for item in task_2:
                    li(raw(item))
            with ol():
                attr(cls='answers')
                for item in answers:
                    li(item)

# ================ EXPORT THE HTML =====================
output_file = filename.split(".")[0] + ".html"
f = open(output_file, 'w')
print(doc, file = f)
# file.write(doc)
f.close()

print('Kanji test has been successfully created as ' + output_file)