import xml.etree.ElementTree as ET
import os
import sys

def resource_path(relative_path): # https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class xml_functions():
    def create_tudu_xml():
        tudu = ET.Element("tudu")
        return tudu

    def save_tudu_xml(new_entry_obj):
        tree = ET.parse(resource_path("tudu.xml"))
        tudu = tree.getroot()

        entry = ET.SubElement(tudu, "entry")
        entry.set("object_id", f"{new_entry_obj.object_id}")

        main_task = ET.SubElement(entry, "task")
        main_task.text = f"{new_entry_obj.task[0]}"
        main_task.set("type", "main")
        main_task.set("state", f"{new_entry_obj.task_state[0]}")

        for index in range(1, len(new_entry_obj.task)):
            sub_task = ET.SubElement(entry, "task")
            sub_task.text = f"{new_entry_obj.task[index]}"
            sub_task.set("type", "sub")
            sub_task.set("state", f"{new_entry_obj.task_state[index]}")
        return tudu

    def load_tudu_xml():
        XML_data = []
        tree = ET.parse(resource_path("tudu.xml"))
        tudu = tree.getroot()

        for entry in tudu.findall("entry"):
            task = []
            task_state = []
            object_id = entry.get("object_id")
            for item in entry.findall("task"):
                task.append(item.text)
                if item.get("state") == "True":
                    task_state.append(True)
                else:
                    task_state.append(False)
            XML_data.append([object_id, task, task_state])
        return XML_data

    def edit_tudu_xml(sender_entry, task_type, task_state):
        tree = ET.parse(resource_path("tudu.xml"))
        tudu = tree.getroot()

        for entry in tudu.findall("entry"):
            object_id = entry.get("object_id")
            if object_id == sender_entry.object_id:
                for task in entry.findall("task"):
                    type = task.get("type")
                    if type == task_type:
                        task.set("state", f"{task_state}")
        return tudu

    def create_settings_xml():
        settings = ET.Element("settings")
        parameter = ET.SubElement(settings, "parameter")
        parameter.text = "task_done_setting"

        return settings

    def save_settings_xml(setting):
        tree = ET.parse(resource_path("settings.xml"))
        settings = tree.getroot()

        for parameter in settings.findall("parameter"):
            if parameter.text == "task_done_setting":
                parameter.set("state", f"{setting}")
        return settings

    def load_settings_xml():
        XML_data = []
        tree = ET.parse(resource_path("settings.xml"))
        settings = tree.getroot()

        for parameter in settings.findall("parameter"):
            parameter_name = parameter.text
            if parameter.get("state") == "True":
                parameter_state = True
            else:
                parameter_state = False
            XML_data.append(parameter_state) 

        return XML_data

    def save_xml(root, root_str):
        xml = ET.ElementTree(root)
        ET.indent(root, space = "\t", level = 0)
        xml.write(resource_path(f"{root_str}.xml"), encoding = "utf-8")