import json

from . import constants

from PyQt5.QtWidgets import QFileDialog


def select_file(parent, title, editor=None):
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        filter="Audio Files (*.wav)",
        options=QFileDialog.DontUseNativeDialog,
    )
    if editor is not None:
        editor.clear()
        editor.setText(file_path)
    return file_path


def select_folder(parent, title, editor=None):
    folder_path = QFileDialog.getExistingDirectory(
        parent,
        title,
        options=QFileDialog.ShowDirsOnly,
    )
    if editor is not None:
        editor.clear()
        editor.setText(folder_path)
    return folder_path


def change_configure(value, relative, configure, path=constants.CONFIGURE_PATH):
    temp_dict = configure

    for key in relative.split(".")[:-1]:
        if key not in temp_dict:
            temp_dict[key] = {}
        temp_dict = temp_dict[key]

    if relative.split("."):
        last_key = relative.split(".")[-1]
        temp_dict[last_key] = value

    with open(path, "w", encoding="utf-8") as cf:
        json.dump(configure, cf, ensure_ascii=False, indent=3)
        cf.close()
