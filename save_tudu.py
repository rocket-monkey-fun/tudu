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

class save_tudu():
    def __init__(self, new_entry_obj):
        self.new_entry = new_entry_obj

    def define_xml_structure(self):
        tree = ET.parse(resource_path("tudu.xml"))
        self.tudu = tree.getroot()

        entry = ET.SubElement(self.tudu, "entry")
        entry.set("object_id", f"{self.new_entry.object_id}")

        main_task = ET.SubElement(entry, "task")
        main_task.text = f"{self.new_entry.task[0]}"
        main_task.set("type", "main")
        main_task.set("state", f"{self.new_entry.task_state[0]}")

        for index in range(1, len(self.new_entry.task)):
            sub_task = ET.SubElement(entry, "task")
            sub_task.text = f"{self.new_entry.task[index]}"
            sub_task.set("type", "sub")
            sub_task.set("state", f"{self.new_entry.task_state[index]}")

    def create_xml(self):
        tudu_xml = ET.ElementTree(self.tudu)
        ET.indent(self.tudu, space = "\t", level = 0)
        tudu_xml.write(resource_path("tudu.xml"), encoding = "utf-8")

class xml_functions():
    def tudu_xml(new_entry_obj):
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

    def save_xml(root, root_str):
        xml = ET.ElementTree(root)
        ET.indent(root, space = "\t", level = 0)
        xml.write(resource_path(f"{root_str}.xml"), encoding = "utf-8")