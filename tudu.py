import dearpygui.dearpygui as dpg
import save_tudu as save
import xml.etree.ElementTree as ET
import colors as col

import uuid
import os
import sys

tab_list = ["TuDu", "Done", "Create"]
sub_task_counter = 1
popup_id_dict = {100: "Text field empty!", 101: "TuDu history not found!"}
task_done_setting = False


def resource_path(relative_path): # https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_uuid():
    id = str(uuid.uuid4())
    return id

################################################################################################################################################################
########## callbacks ##########
################################################################################################################################################################

def callback_add_sub_task_button(sender, app_data):
    global sub_task_counter
    sub_task_counter += 1
    dpg.add_input_text(parent = "create_tab", before = "add_remove_group", hint = "Sub task", indent = 10, width = 270, tag = f"sub_task_{sub_task_counter}")

def callback_remove_sub_task_button(sender, app_data):
    global sub_task_counter
    dpg.delete_item(f"sub_task_{sub_task_counter}")
    sub_task_counter -= 1

def callback_add_tudu_button(sender, app_data):
    if not check_empty_fields():
        show_popup(popup_id = 100)
        return

    new_entry_obj = tudu_entry_UI()
    tudu = save.xml_functions.tudu_xml(new_entry_obj)
    save.xml_functions.save_xml(tudu, "tudu")
    create_tudu_ui(new_entry_obj)
    clear_create_tab()

################################################################################################################################################################
########## functions ##########
################################################################################################################################################################

def check_empty_fields():
    child_items = dpg.get_item_children("create_group", 1)
    for item in child_items:
        item_type = dpg.get_item_type(item)
        if item_type == "mvAppItemType::mvInputText":
            if dpg.get_value(item) == "":
                return False
    return True

def show_popup(popup_id):
    with dpg.window(popup = True, modal = True, no_close = True, no_resize = True, label = "Warning!", pos = (20, 20), tag = "popup_window"):
        string = popup_id_dict.get(popup_id)
        dpg.add_text(string)
        dpg.add_text("")
        dpg.add_button(label = "OK", callback = lambda: dpg.delete_item("popup_window"))

def show_settings_window():
    with dpg.window(popup = True, modal = True, no_close = True, no_resize = True, label = "Settings", pos = (20, 20)):
        dpg.add_text("Task Done if all subtasks are done", bullet = True)
        dpg.add_radio_button((True, False), indent = 10, horizontal = True, default_value = task_done_setting, callback = change_task_done_setting)
        dpg.add_separator()
        dpg.add_button(label = "OK", callback = lambda: dpg.hide_item(dpg.get_item_parent(dpg.last_item())))

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

def change_task_state(sender, app_data, user_data):
    change_task_state_UI(sender, app_data, user_data)
    change_task_state_XML(sender, app_data, user_data)

def change_task_state_UI(sender, app_data, user_data):
    if app_data == True:
        parent_1_up = dpg.get_item_parent(sender)
        parent_2_up = dpg.get_item_parent(parent_1_up)
        child_elements_1_down = dpg.get_item_children(parent_2_up, 1)
        filtered_elements_1_down = []
        filtered_elements_2_down = []

        for item in child_elements_1_down:
            if dpg.get_item_type(item) == "mvAppItemType::mvGroup":
                filtered_elements_1_down.append(item)
        
        for item in filtered_elements_1_down:
            child_elements_2_down = dpg.get_item_children(item, 1)
            
            for item in child_elements_2_down:
                if dpg.get_item_type(item) == "mvAppItemType::mvCheckbox":
                    filtered_elements_2_down.append(item)

        if sender == filtered_elements_2_down[0]:
            dpg.delete_item(user_data[0].object_id)
            create_done_ui(user_data[0])
        else:
            if task_done_setting == True:
                for item in range(1, len(filtered_elements_2_down)):
                    if dpg.get_value(filtered_elements_2_down[item]) == False:
                        return
                    else: 
                        continue
                change_task_state_XML(None, True, [user_data[0], "main"])
                dpg.delete_item(user_data[0].object_id)
                create_done_ui(user_data[0])

            if task_done_setting == False:
                return

def create_done_ui(new_entry_obj):
    with dpg.group(parent = "done_tab", tag = new_entry_obj.object_id):
        dpg.add_text(new_entry_obj.task[0], bullet = True, indent = 0, color = col.retro_turqoise)
        for index in range(1, len(new_entry_obj.task)):
            dpg.add_text(new_entry_obj.task[index], bullet = True, indent = 10, color = col.retro_turqoise)
        dpg.add_separator()
        dpg.add_separator()

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
                    tudu_xml.write(resource_path("tudu.xml"), encoding = "utf-8")

def change_task_done_setting(sender, app_data):
    global task_done_setting
    if app_data == "True":
        task_done_setting = True
    else:
        task_done_setting = False
    save_setting_xml()
    print(task_done_setting)

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

def save_setting_xml():
    tree = ET.parse(resource_path("settings.xml"))
    settings = tree.getroot()
    for parameter in settings.findall("parameter"):
        if parameter.text == "task_done_setting":
            parameter.set("state", f"{task_done_setting}")

    save.xml_functions.save_xml(settings, "settings")

    #settings_xml = ET.ElementTree(settings)
    #ET.indent(settings, space = "\t", level = 0)
    #settings_xml.write(resource_path("settings.xml"), encoding = "utf-8")

################################################################################################################################################################
########## UI ##########
################################################################################################################################################################

def define_GUI():
    dpg.create_context()
    dpg.create_viewport(title = "TuDu", always_on_top = True, width = 300, height = 500, small_icon = resource_path("resources\icon.ico"), large_icon = resource_path("resources\icon.ico"))

    with dpg.window(tag = "main_window"):

        with dpg.menu_bar():
            dpg.add_button(label = "Settings", callback = show_settings_window)

        with dpg.tab_bar():
            dpg.add_tab(label = tab_list[0], tag = "tudu_tab")
            dpg.add_tab(label = tab_list[1], tag = "done_tab")
            dpg.add_tab(label = tab_list[2], tag = "create_tab")
            define_create_tab()
            load_entries()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    #dpg.set_exit_callback(callback = save_setting_xml)
    dpg.start_dearpygui()
    dpg.destroy_context()

def define_create_tab():
    with dpg.group(parent = "create_tab", tag = "create_group"):
        dpg.add_input_text(hint = "Main task", width = 280, tag = "main_task")
        dpg.add_input_text(hint = "Sub task", indent = 10, width = 270, tag = "sub_task_1")
        with dpg.group(horizontal = True, tag = "add_remove_group"):
            dpg.add_button(label = "+", indent = 10, callback = callback_add_sub_task_button, tag = "add_sub_task_button")
            dpg.add_button(label = "-", indent = 30, callback = callback_remove_sub_task_button, tag = "remove_sub_task_button")
        dpg.add_separator()
        dpg.add_button(label = "Add TuDu", callback = callback_add_tudu_button, tag = "add_tudu_button")

def load_entries():
    if os.path.isfile(resource_path("tudu.xml")):
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
        show_popup(popup_id = 101)
        tudu = ET.Element("tudu")
        tudu_xml = ET.ElementTree(tudu)
        ET.indent(tudu, space = "\t", level = 0)
        tudu_xml.write(resource_path("tudu.xml"), encoding = "utf-8")

define_GUI()

