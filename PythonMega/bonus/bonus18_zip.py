import PySimpleGUI as sg
from zip_extractor import extractor_archive
sg.theme('Black')

label1 = sg.Text('Select archive')
input1 = sg.Input()
chose_button1 = sg.FileBrowse('Choose', key='archive')

label2 = sg.Text('Select directory')
input2 = sg.Input()
chose_button2 = sg.FolderBrowse('Choose', key='folder')

extract_button = sg.Button('Extract')
output_label = sg.Text(key='output', text_color='green')

window = sg.Window("Archive Extractor0",
                   layout=[[label1, input1, chose_button1],
                           [label2, input2, chose_button2],
                            [extract_button, output_label]])


while True:
    event, values = window.read()
    print(event, values)
    archivepath = values["archive"]
    dest_dir = values["folder"]
    extractor_archive(archivepath, dest_dir)
    window["output"].update(value='Extraction Completed' )

window.close()

