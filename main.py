import tkinter as tk
from tkinter import filedialog
from tkinter import Button


def print_localised_surnames():
    file_path = filedialog.askopenfilename()

    if file_path is None or file_path == '':
        return

    # get only the lines with "name = ..."
    lines = [line for line in open(file_path) if "name" in line]
    # cut everything to the left of "=", remove quotes and line breaks
    lines = [line.partition("= ")[2]
                 .replace("\"", "")
                 .rstrip('\n') for line in lines]

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        lines = ["{0}: \"{1}\"\n".format(line, line.replace("dynn_", "")) for line in lines]

        save_file.writelines(lines)


def print_localised_titles():
    file_path = filedialog.askopenfilename()

    if file_path is None or file_path == '':
        return

    title_types = ('e', 'k', 'd', 'c', 'b')
    title_names = {
        'e': 'Empires',
        'k': 'Kingdoms',
        'd': 'Duchies',
        'c': 'Counties',
        'b': 'Baronies'
    }

    prefixes = tuple("{}_".format(title_type) for title_type in title_types)

    lines = [line.lstrip() for line in open(file_path)]
    new_lines = []

    for line in lines:
        if line.startswith(prefixes):
            new_lines.append(line)
        elif line.startswith("capital = "):
            new_lines.append(line.replace("capital = ", "").rstrip())

    lines = [line.partition(" ")[0] for line in new_lines]
    print(lines)
    lines = [line.partition("_") for line in set(lines)]
    print(lines)

    title_groups = {}

    for line in lines:
        title_type = line[0]
        title_name = line[2]

        if title_type not in title_groups.keys():
            title_groups[title_type] = []

        title_groups[title_type].append(title_name)

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        for title_type in title_types:
            title_collection = []

            for title in title_groups[title_type]:
                title_id = "{}_{}".format(title_type, title)
                localised_title = title.replace("_", " ").title() # capitalise and replace underscores

                title_collection.append("{}: \"{}\"\n".format(title_id, localised_title))

            save_file.write("#{}\n".format(title_names[title_type]))
            save_file.writelines(sorted(title_collection))


root = tk.Tk()

buttons = [
    Button(root, text="Localize surnames", command=print_localised_surnames),
    Button(root, text="Localize titles", command=print_localised_titles)
]

for button in buttons:
    button.pack()

root.mainloop()
