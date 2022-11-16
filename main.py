import tkinter as tk
from tkinter import filedialog, Button, Radiobutton

from enum import Enum

from typing import Union, Callable, Iterable, Mapping

from os import listdir
from os.path import isfile, join, basename

import itertools


class SelectionMode(Enum):
    SINGLE = 1
    FOLDER = 2


def change_selection_mode(new_mode: SelectionMode):
    global selectionMode
    selectionMode = new_mode


def join_file_contents(src: Mapping[str, Iterable[str]]) -> Iterable[str]:
    return itertools.chain(*src.values())


def preprocess_input(src: Mapping[str, Iterable[str]]) -> Mapping[str, Iterable[str]]:
    src = {file_name: [line.strip() for line in file_content] for (file_name, file_content) in src.items()}

    return src


def postprocess_output(src_lines: Iterable[str]) -> Iterable[str]:
    lines = [line + '\n' if line.startswith('#')
             else ' {0}\n'.format(line) for line in src_lines]

    return lines


def localise_surnames(src: Mapping[str, Iterable[str]]) -> Iterable[str]:
    src_lines = join_file_contents(src)

    # get only the lines with "name = ..."
    # cut everything to the left of "=", remove quotes
    lines = [line[7:].replace('"', '')
             for line in src_lines if line.startswith('name = ')]

    # line[5:] cuts off the dynn_ prefix
    lines = ['{0}: "{1}"'.format(line, line[5:]) for line in lines]

    return lines


def localise_titles(src: Mapping[str, Iterable[str]]) -> Iterable[str]:
    src_lines = join_file_contents(src)

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


def localise_forenames(src: Mapping[str, Iterable[str]]) -> Iterable[str]:
    src_lines = join_file_contents(src)

    lines = [line.split(' ') for line in src_lines if line.startswith('name =')]
    names = [line[2].strip('"') for line in lines]  # [name, =, "name", comment]
    names = ['{0}: "{0}"'.format(name) for name in sorted(set(names))]

    return names


def localise_history(src: Mapping[str, Iterable[str]]) -> Iterable[str]:
    result = {}

    for file_name, file_content in src.items():
        name = file_name.split('.')[0]
        culture = next((line for line in file_content if line.startswith("culture")), 'culture = none')
        religion = next((line for line in file_content if line.startswith("religion")), 'religion = none')

        result[int(name)] = ("{0} = {{\n"
                             "\t{1}\n"
                             "\t{2}\n"
                             "\tholding = none\n"
                             "}}\n".format(name, culture, religion))

    lines = []

    for i in sorted(result.keys()):
        lines.append(result[i])

    return lines


def main_loop(selection_mode: tk.IntVar, process_function: Union[Callable, None], postprocess: bool):
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

    file_contents = {}

    if selection_mode.get() == SelectionMode.SINGLE.value:
        file_contents[basename(file_location)] = open(file_location).readlines()
    elif selection_mode.get() == SelectionMode.FOLDER.value:
        for file_name in listdir(file_location):
            full_path = join(file_location, file_name)

            if not isfile(full_path) or file_name == '.DS_Store':
                continue

            file_contents[file_name] = open(full_path).readlines()
    else:
        return

    result = process_function(preprocess_input(file_contents))

    if postprocess:
        result = postprocess_output(result)

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        save_file.writelines(result)


window = tk.Tk()
selectionMode = tk.IntVar(None, SelectionMode.SINGLE.value)

buttons = [
    [
        Radiobutton(window, text='Single file mode', variable=selectionMode, value=SelectionMode.SINGLE.value),
        Radiobutton(window, text='Folder mode', variable=selectionMode, value=SelectionMode.FOLDER.value),
    ], [
        Button(window, text='Localize surnames', command=lambda: main_loop(selectionMode, localise_surnames, True)),
        Button(window, text='Localize forenames', command=lambda: main_loop(selectionMode, localise_forenames, True)),
        Button(window, text='Localize titles', command=lambda: main_loop(selectionMode, localise_titles, True)),
        Button(window, text='Localize history', command=lambda: main_loop(selectionMode, localise_history, False)),
    ]
]

for group_index in range(len(buttons)):
    for button_index in range(len(buttons[group_index])):
        buttons[group_index][button_index].grid(row=group_index, column=button_index, ipadx=5, padx=5, pady=5)

window.title("amazing pro mlg utilita from russia with love")
window.mainloop()
