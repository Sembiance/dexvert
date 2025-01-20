import PySimpleGUI as sg
from ps2ico import Ps2ico
from ps2sys import Ps2sys
from ico2gltf import export_gltf
from pathlib import Path

def main():
    sg.theme("Reddit")

    layout = [
        [sg.Text("Input file (.ico)")],
        [sg.Input(key="input"), sg.FileBrowse(target="input", button_text="Browse", file_types=(("Icon Files", "*.ico"), ("All Files", "*.*")))],

        [sg.Text("Metadata (icon.sys, optional)")],
        [sg.Input(key="metadata"), sg.FileBrowse(target="metadata", button_text="Browse", file_types=(("icon.sys", "icon.sys"), ("All Files", "*.*")))],
        [],
        [sg.Text("Output file (.glb or .gltf)")],
        [sg.Input(key="output"), sg.SaveAs(target="output", button_text="Browse", file_types=(("Binary glTF File", "*.glb"), ("glTF File", "*.gltf")))],

        [sg.Button("Convert"), sg.Text(key="message", text_color="red", size=(30, None))] 
    ]

    window = sg.Window("ico2gltf", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "Convert":
            input_path = Path(values["input"])
            output_path = Path(values["output"])

            metadata = None

            window["message"].update(text_color="red")
            window["message"].update("")

            if not input_path.is_file() or not input_path.exists():
                window["message"].update("Input file doesn't exit")
                continue
            
            if values["metadata"] != "":
                metadata_path = Path(values["metadata"])

                if not metadata_path.is_file() or not metadata_path.exists():
                    window["message"].update("Metadata file doesn't exit")
                    continue

            try:
                if values["metadata"] != "":
                    metadata = Ps2sys.from_file(values["metadata"])

                icon = Ps2ico.from_file(values["input"])
                export_gltf(icon, values["output"], metadata)
            except Exception:
                window["message"].update("An error has occured")
                continue

            window["message"].update("File converted successfuly")
            window["message"].update(text_color="green")

    window.close()

if __name__ == "__main__":
	main()