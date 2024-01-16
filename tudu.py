import dearpygui.dearpygui as dpg
import save_tudu as save
import xml.etree.ElementTree as ET
import colors as col

import uuid
import os
import sys

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

tab_list = ["TuDu", "Done", "Create"]
sub_task_counter = 1
popup_id_dict = {100: "Text field empty!"}

def create_uuid():
    id = str(uuid.uuid4())
    return id

def add_sub_task_button(sender, app_data):
    global sub_task_counter
    sub_task_counter += 1
    dpg.add_input_text(parent = "create_tab", before = "add_remove_group", hint = "Sub task", indent = 10, width = 270, tag = f"sub_task_{sub_task_counter}")

def remove_sub_task_button(sender, app_data):
    global sub_task_counter
    dpg.delete_item(f"sub_task_{sub_task_counter}")
    sub_task_counter -= 1

def add_tudu_button(sender, app_data):
    if not check_empty_fields():
        show_popup(popup_id = 100)
        return

    new_entry_obj = tudu_entry_UI()
    new_entry_xml = save.save_tudu(new_entry_obj)
    new_entry_xml.define_xml_structure()
    new_entry_xml.create_xml()
    create_tudu_ui(new_entry_obj)
    clear_create_tab()

def check_empty_fields():
    child_items = dpg.get_item_children("create_group", 1)
    for item in child_items:
        item_type = dpg.get_item_type(item)
        if item_type == "mvAppItemType::mvInputText":
            if dpg.get_value(item) == "":
                return False
    return True

def show_popup(popup_id = 100):
    with dpg.window(popup = True, modal = True, no_close = True, no_resize = True, label = "Warning!", pos = (20, 20), tag = "popup_window"):
        string = popup_id_dict.get(popup_id)
        dpg.add_text(string)
        dpg.add_text("")
        dpg.add_button(label = "OK", callback = lambda: dpg.delete_item("popup_window"))

def clear_create_tab():
    global sub_task_counter
    sub_task_counter = 1

    dpg.delete_item("create_group")
    define_create_tab()

def create_tudu_ui(new_entry_obj):
    with dpg.group(parent = "tudu_tab", tag = new_entry_obj.object_id):
        with dpg.group(horizontal = True):
            dpg.add_checkbox(indent = 0, default_value = new_entry_obj.task_state[0], user_data = [new_entry_obj, "main"], callback = change_task_state)
            dpg.add_text(new_entry_obj.task[0], indent = 30, color = col.retro_orange)
        for index in range(1, len(new_entry_obj.task)):
            with dpg.group(horizontal = True):
                dpg.add_checkbox(indent = 10, default_value = new_entry_obj.task_state[index], user_data = [new_entry_obj, "sub"], callback = change_task_state)
                dpg.add_text(new_entry_obj.task[index], indent = 40, color = col.retro_orange)
        dpg.add_separator()
        dpg.add_separator()

def create_done_ui(new_entry_obj):
    with dpg.group(parent = "done_tab", tag = new_entry_obj.object_id):
        dpg.add_text(new_entry_obj.task[0], bullet = True, indent = 0, color = col.retro_turqoise)
        for index in range(1, len(new_entry_obj.task)):
            dpg.add_text(new_entry_obj.task[index], bullet = True, indent = 10, color = col.retro_turqoise)
        dpg.add_separator()
        dpg.add_separator()

def change_task_state(sender, app_data, user_data):
    change_task_state_UI(sender, app_data, user_data)
    change_task_state_XML(sender, app_data, user_data)

def change_task_state_UI(sender, app_data, user_data):
    if app_data == True and user_data[1] == "main":
        dpg.delete_item(user_data[0].object_id)
        create_done_ui(user_data[0])

def change_task_state_XML(sender, app_data, user_data):
    tree = ET.parse(resource_path("tudu.xml"))
    tudu = tree.getroot()
    for entry in tudu.findall("entry"):
        object_id = entry.get("object_id")
        if object_id == user_data[0].object_id:
            for task in entry.findall("task"):
                type = task.get("type")
                if type == user_data[1]:
                    task.set("state", f"{app_data}")

                    tudu_xml = ET.ElementTree(tudu)
                    ET.indent(tudu, space = "\t", level = 0)
                    tudu_xml.write(resource_path("tudu.xml", encoding = "utf-8"))

def str_to_bool(string):
    if string == "True":
        return True
    else:
        return False

class tudu_entry_UI():
    def __init__(self):
        self.object_id = create_uuid()
        self.task = [dpg.get_value("main_task")]
        for item in [dpg.get_value(sub_task) for sub_task in (f"sub_task_{sub_task_number}" for sub_task_number in range(1, sub_task_counter + 1))]:
            self.task.append(item)
        self.task_state = [False]
        for item in [False for state in range(1, sub_task_counter + 1)]:
            self.task_state.append(item)

class tudu_entry_XML():
    def __init__(self, XML_data):
        self.object_id = XML_data[0]
        self.task = XML_data[1]
        self.task_state = XML_data[2]

################################################################################################################################################################
########## UI ##########
################################################################################################################################################################

def define_GUI():
    dpg.create_context()
    dpg.create_viewport(title = "TuDu", always_on_top = True, width = 300, height = 500)

    with dpg.window(tag = "main_window"):

        with dpg.tab_bar():
            dpg.add_tab(label = tab_list[0], tag = "tudu_tab")
            dpg.add_tab(label = tab_list[1], tag = "done_tab")
            dpg.add_tab(label = tab_list[2], tag = "create_tab")
            define_create_tab()
            load_entries()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

def define_create_tab():
    with dpg.group(parent = "create_tab", tag = "create_group"):
        dpg.add_input_text(hint = "Main task", width = 280, tag = "main_task")
        dpg.add_input_text(hint = "Sub task", indent = 10, width = 270, tag = "sub_task_1")
        with dpg.group(horizontal = True, tag = "add_remove_group"):
            dpg.add_button(label = "+", indent = 10, callback = add_sub_task_button, tag = "add_sub_task_button")
            dpg.add_button(label = "-", indent = 30, callback = remove_sub_task_button, tag = "remove_sub_task_button")
        dpg.add_separator()
        dpg.add_button(label = "Add TuDu", callback = add_tudu_button, tag = "add_tudu_button")

def load_entries():
    if os.path.isfile("tudu.xml"):
        tree = ET.parse(resource_path("tudu.xml"))
        tudu = tree.getroot()
        for entry in tudu.findall("entry"):
            task = []
            task_state = []
            object_id = entry.get("object_id")
            for item in entry.findall("task"):
                task.append(item.text)
                task_state.append(str_to_bool(item.get("state")))
            XML_data = [object_id, task, task_state]
            new_entry_obj = tudu_entry_XML(XML_data)
            if task_state[0] != True:
                create_tudu_ui(new_entry_obj)
            if task_state[0] == True:
                create_done_ui(new_entry_obj)
    else:
        print("test")

define_GUI()

