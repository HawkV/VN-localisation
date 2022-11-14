import tkinter as tk
from tkinter import filedialog
from tkinter import Button

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


selectionMode = SelectionMode.FOLDER


def change_selection_mode(new_mode: SelectionMode):
    global selectionMode
    selectionMode = new_mode


processFunction = None


def change_process_function(process_function: Callable):
    global processFunction
    processFunction = process_function


def preprocess_input(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [line.strip() for line in src_lines]

    return lines


def postprocess_output(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [' {0}\n'.format(line) for line in src_lines if not line.startswith('#')]

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
    lines = [line.strip() for line in src_lines]

    title_names = {
        'e': 'Empires',
        'k': 'Kingdoms',
        'd': 'Duchies',
        'c': 'Counties',
        'b': 'Baronies'
    }
    title_types = title_names.keys()
    prefixes = tuple("{0}_".format(title_type) for title_type in title_types)

    new_lines = []

    for line in lines:
        if line.startswith(prefixes):
            new_lines.append(line)
        elif line.startswith('capital = '):
            new_lines.append(line.replace('capital = ', ''))

    lines = [line.partition(' ')[0] for line in new_lines]
    lines = [line.partition('_') for line in set(lines)]

    title_groups = {}

    result = []

    for line in lines:
        title_type = line[0]
        title_name = line[2]

        if title_type not in title_groups.keys():
            title_groups[title_type] = []

        title_groups[title_type].append(title_name)

        for title_type in title_types:
            title_collection = []

            for title in title_groups[title_type]:
                title_id = '{0}_{1}'.format(title_type, title)
                localised_title = title.replace('_', ' ').title()  # capitalise and replace underscores

                title_collection.append('{0}: "{1}"'.format(title_id, localised_title))

            result.append('#{0}'.format(title_names[title_type]))
            result.extend(sorted(title_collection))

    return result


def main_loop(selection_mode: SelectionMode, process_function: Union[Callable, None]):
    if process_function is None:
        return

    if selection_mode == SelectionMode.SINGLE:
        file_location = filedialog.askopenfilename()
    elif selection_mode == SelectionMode.FOLDER:
        file_location = filedialog.askdirectory()
    else:
        return

    if file_location is None or file_location == '':
        return

    if selection_mode == SelectionMode.SINGLE:
        lines = open(file_location).readlines()
    elif selection_mode == SelectionMode.FOLDER:
        files = [full_path for file_name in listdir(file_location)
                 if isfile(full_path := join(file_location, file_name))]

        lines = itertools.chain(*[open(file_path).readlines() for file_path in files])
    else:
        return

    result = postprocess_output(process_function(preprocess_input(lines)))

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        save_file.writelines(result)


root = tk.Tk()

mode_buttons = [
    Button(root, text='Single file mode', command=lambda: change_selection_mode(SelectionMode.SINGLE)),
    Button(root, text='Folder mode', command=lambda: change_selection_mode(SelectionMode.FOLDER))
]

function_buttons = [
    Button(root, text='Localize surnames', command=lambda: main_loop(selectionMode, localise_surnames)),
    Button(root, text='Localize titles', command=lambda: main_loop(selectionMode, localise_titles))
]

for button in mode_buttons + function_buttons:
    button.pack()

root.mainloop()
