import tkinter as tk
from tkinter import filedialog
from tkinter import Button
from tkinter import Radiobutton
from tkinter import Frame

from enum import Enum

from typing import Union
from typing import Callable
from typing import Iterable

from os import listdir
from os.path import isfile, join

import itertools


class SelectionMode(Enum):
    SINGLE = 1
    FOLDER = 2


def change_selection_mode(new_mode: SelectionMode):
    global selectionMode
    selectionMode = new_mode


def preprocess_input(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [line.strip() for line in src_lines]

    return lines


def postprocess_output(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [line + '\n' if line.startswith('#')
             else ' {0}\n'.format(line) for line in src_lines]

    return lines


def localise_surnames(src_lines: Iterable[str]) -> Iterable[str]:
    # get only the lines with "name = ..."
    # cut everything to the left of "=", remove quotes
    lines = [line[7:].replace('"', '')
             for line in src_lines if line.startswith('name = ')]

    # line[5:] cuts off the dynn_ prefix
    lines = ['{0}: "{1}"'.format(line, line[5:]) for line in lines]

    return lines


def localise_titles(src_lines: Iterable[str]) -> Iterable[str]:
    title_names = {
        'e': 'Empires',
        'k': 'Kingdoms',
        'd': 'Duchies',
        'c': 'Counties',
        'b': 'Baronies',
        'cn': 'Cultural names',
    }
    title_types = title_names.keys()
    prefixes = tuple("{0}_".format(title_type) for title_type in title_types)

    words = []

    for line in src_lines:
        words.extend(word for word in line.split(' ') if word.startswith(prefixes))

    words = [word.split('_', 1) for word in set(words)]

    title_groups = {}

    result = []

    for word in words:
        title_type = word[0]
        title_name = word[1]

        if title_type not in title_groups.keys():
            title_groups[title_type] = []

        title_groups[title_type].append(title_name)

    for title_type in title_types:
        if title_type not in title_groups:
            continue

        title_collection = []

        for title in title_groups[title_type]:
            title_id = '{0}_{1}'.format(title_type, title)
            localised_title = title.replace('_', ' ').title()  # capitalise and replace underscores

            title_collection.append('{0}: "{1}"'.format(title_id, localised_title))

        result.append('#{0}'.format(title_names[title_type]))
        result.extend(sorted(title_collection))

    return result


def localise_forenames(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [line.split(' ') for line in src_lines if line.startswith('name =')]
    names = [line[2].strip('"') for line in lines]  # [name, =, "name", comment]
    names = ['{0}: "{0}"'.format(name) for name in sorted(set(names))]

    return names


def localise_history(src_lines: Iterable[str]) -> Iterable[str]:
    return []


def main_loop(selection_mode: tk.IntVar, process_function: Union[Callable, None]):
    if process_function is None:
        return

    if selection_mode.get() == SelectionMode.SINGLE.value:
        file_location = filedialog.askopenfilename()
    elif selection_mode.get() == SelectionMode.FOLDER.value:
        file_location = filedialog.askdirectory()
    else:
        return

    if file_location is None or file_location == '':
        return

    if selection_mode.get() == SelectionMode.SINGLE.value:
        lines = open(file_location).readlines()
    elif selection_mode.get() == SelectionMode.FOLDER.value:
        files = [full_path for file_name in listdir(file_location)
                 if isfile(full_path := join(file_location, file_name))]

        lines = itertools.chain(*[open(file_path).readlines() for file_path in files])
    else:
        return

    result = postprocess_output(process_function(preprocess_input(lines)))

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        save_file.writelines(result)


window = tk.Tk()
selectionMode = tk.IntVar(None, SelectionMode.SINGLE.value)

buttons = [
    [
        Radiobutton(window, text='Single file mode', variable=selectionMode, value=SelectionMode.SINGLE.value),
        Radiobutton(window, text='Folder mode', variable=selectionMode, value=SelectionMode.FOLDER.value),
    ], [
        Button(window, text='Localize surnames', command=lambda: main_loop(selectionMode, localise_surnames)),
        Button(window, text='Localize forenames', command=lambda: main_loop(selectionMode, localise_forenames)),
        Button(window, text='Localize titles', command=lambda: main_loop(selectionMode, localise_titles)),
        Button(window, text='Localize history', command=lambda: main_loop(selectionMode, localise_history)),
    ]
]

for group_index in range(len(buttons)):
    for button_index in range(len(buttons[group_index])):
        buttons[group_index][button_index].grid(row=group_index, column=button_index, ipadx=5, padx=5, pady=5)

window.title("amazing pro mlg utilita from russia with love")
window.mainloop()
