import dearpygui.dearpygui as dpg
import xml_changes as xml
import colors as col

import uuid
import os
import sys
import time

tab_list = ["TuDu", "Done", "Create"]
sub_task_counter = 1
popup_id_dict = {100: "Text field empty!", 101: "TuDu history not found!", 102: "Settings not found!"}
task_done_setting = True
create_sub_task = True


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

    new_tudu_item = tudu_item_UI()
    tudu = xml.xml_functions.save_tudu_xml(new_tudu_item)
    xml.xml_functions.save_xml(tudu, "tudu")
    create_tudu_ui(new_tudu_item)
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
        dpg.add_text("Create Sub task with Main task", bullet = True)
        dpg.add_radio_button((True, False), indent = 10, horizontal = True, default_value = create_sub_task, callback = change_create_sub_task_setting)
        dpg.add_button(label = "OK", callback = lambda: dpg.hide_item(dpg.get_item_parent(dpg.last_item())))

def clear_create_tab():
    global sub_task_counter
    sub_task_counter = 1
    dpg.delete_item("create_group")
    define_create_tab()

def create_tudu_ui(new_tudu_item):
    with dpg.group(parent = "tudu_tab", tag = new_tudu_item.object_id):
        with dpg.group(horizontal = True):
            dpg.add_checkbox(indent = 0, default_value = new_tudu_item.task_state[0], user_data = [new_tudu_item, "main"], callback = change_task_state)
            dpg.add_text(new_tudu_item.task[0], indent = 30, color = col.retro_orange)
        for index in range(1, len(new_tudu_item.task)):
            with dpg.group(horizontal = True):
                dpg.add_checkbox(indent = 10, default_value = new_tudu_item.task_state[index], user_data = [new_tudu_item, "sub"], callback = change_task_state)
                dpg.add_text(new_tudu_item.task[index], indent = 40, color = col.retro_orange)
        dpg.add_separator()
        dpg.add_separator()

def change_task_state(sender, app_data, user_data):
    change_task_state_UI(sender, app_data, user_data)

    tudu = xml.xml_functions.edit_tudu_xml(user_data[0], user_data[1], app_data)
    xml.xml_functions.save_xml(tudu, "tudu")


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

                tudu = xml.xml_functions.edit_tudu_xml(user_data[0], "main", True)
                xml.xml_functions.save_xml(tudu, "tudu")
                dpg.delete_item(user_data[0].object_id)
                create_done_ui(user_data[0])

            if task_done_setting == False:
                return

def create_done_ui(new_tudu_item):
    with dpg.group(parent = "done_tab", tag = new_tudu_item.object_id):
        dpg.add_text(new_tudu_item.task[0], bullet = True, indent = 0, color = col.retro_turqoise)
        for index in range(1, len(new_tudu_item.task)):
            dpg.add_text(new_tudu_item.task[index], bullet = True, indent = 10, color = col.retro_turqoise)
        dpg.add_separator()
        dpg.add_separator()

def change_task_done_setting(sender, app_data):
    global task_done_setting
    if app_data == "True":
        task_done_setting = True
    else:
        task_done_setting = False
    print(task_done_setting)
    settings = xml.xml_functions.save_settings_xml(task_done_setting)
    xml.xml_functions.save_xml(settings, "settings")

def change_create_sub_task_setting(sender, app_data):
    global create_sub_task
    if app_data == "True":
        create_sub_task = True
    else:
        create_sub_task = False
    print(create_sub_task)
    settings = xml.xml_functions.save_settings_xml(create_sub_task)
    xml.xml_functions.save_xml(settings, "settings")

class tudu_item_UI():
    def __init__(self):
        self.object_id = create_uuid()
        self.task = [dpg.get_value("main_task")]
        for item in [dpg.get_value(sub_task) for sub_task in (f"sub_task_{sub_task_number}" for sub_task_number in range(1, sub_task_counter + 1))]:
            self.task.append(item)
        self.task_state = [False]
        for item in [False for state in range(1, sub_task_counter + 1)]:
            self.task_state.append(item)

class tudu_item_XML():
    def __init__(self, XML_data):
        self.object_id = XML_data[0]
        self.task = XML_data[1]
        self.task_state = XML_data[2]

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
            load_settings()

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
            dpg.add_button(label = "+", indent = 10, callback = callback_add_sub_task_button, tag = "add_sub_task_button")
            dpg.add_button(label = "-", indent = 30, callback = callback_remove_sub_task_button, tag = "remove_sub_task_button")
        dpg.add_separator()
        dpg.add_button(label = "Add TuDu", callback = callback_add_tudu_button, tag = "add_tudu_button")

def load_entries():
    if os.path.isfile(resource_path("tudu.xml")):
        XML_data = xml.xml_functions.load_tudu_xml()
        for index in range(0, len(XML_data)):
            new_tudu_item = tudu_item_XML(XML_data[index])
            if XML_data[index][2][0] == False:
                create_tudu_ui(new_tudu_item)
            if XML_data[index][2][0] == True:
                create_done_ui(new_tudu_item)
    else:
        show_popup(popup_id = 101)
        tudu = xml.xml_functions.create_tudu_xml()
        xml.xml_functions.save_xml(tudu, "tudu")

def load_settings():
    global task_done_setting
    if os.path.isfile(resource_path("settings.xml")):
        XML_data = xml.xml_functions.load_settings_xml()
        task_done_setting = XML_data[0]
    else:
        show_popup(popup_id = 102)
        settings = xml.xml_functions.create_settings_xml()
        xml.xml_functions.save_xml(settings, "settings")
        create_stuff()

def create_stuff():
        settings_1 = xml.xml_functions.save_settings_xml(task_done_setting)  
        xml.xml_functions.save_xml(settings_1, "settings")

define_GUI()

