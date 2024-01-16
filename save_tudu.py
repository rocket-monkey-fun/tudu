import xml.etree.ElementTree as ET

class save_tudu():
    def __init__(self, new_entry_obj):
        self.new_entry = new_entry_obj

    def define_xml_structure(self):
        tree = ET.parse('tudu.xml')
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
        tudu_xml.write("tudu.xml", encoding = "utf-8")