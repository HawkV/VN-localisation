import tkinter as tk
from tkinter import filedialog


def print_localised_surnames():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    # get only the lines with "name = ..."
    lines = [line for line in open(file_path) if "name" in line]
    # cut everything to the left of "=", remove quotes and line breaks
    lines = [line.partition("= ")[2]
                 .replace("\"", "")
                 .rstrip('\n') for line in lines]

    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as save_file:
        if save_file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return

        lines = ["{0}: \"{1}\"\n".format(line, line.replace("dynn_", "")) for line in lines]

        save_file.writelines(lines)


print_localised_surnames()
