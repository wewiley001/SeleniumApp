import os
import tkinter as tk
from tkinter import messagebox
import inspect
import threading
import time
import functions

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Load available functions with docs and args
available_functions = {
    name: func
    for name, func in inspect.getmembers(functions, inspect.isfunction)
}

function_args = {
    name: list(inspect.signature(func).parameters.keys())[1:]
    for name, func in available_functions.items()
}

function_docs = {
    name: func.__doc__ or "No description provided."
    for name, func in available_functions.items()
}

queue_slots = []
stop_event = threading.Event()

def get_driver(browser_name):
    if browser_name == "Chrome":
        return webdriver.Chrome(options=ChromeOptions())
    elif browser_name == "Firefox":
        return webdriver.Firefox(options=FirefoxOptions())
    elif browser_name == "Edge":
        return webdriver.Edge(options=EdgeOptions())
    else:
        raise Exception(f"Unsupported browser: {browser_name}")

def show_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry("+%d+%d" % (widget.winfo_rootx() + 20, widget.winfo_rooty() + 20))
    label = tk.Label(tooltip, text=text, justify='left', background='lightyellow',
                     relief='solid', borderwidth=1, wraplength=300)
    label.pack(ipadx=1)
    widget.tooltip_window = tooltip

def hide_tooltip(widget):
    if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
        widget.tooltip_window.destroy()
        widget.tooltip_window = None

def run_queue():
    browser = browser_choice.get()
    url = url_input.get().strip()
    run_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    stop_event.clear()

    if not url.startswith("http"):
        messagebox.showerror("Error", "Please enter a valid URL starting with http or https.")
        run_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        return

    open_url_slot = {
        "func_var": tk.StringVar(value="open_url"),
        "enabled_var": tk.BooleanVar(value=True),
        "delay_var": tk.StringVar(value="0"),
        "inputs": {"url": tk.StringVar(value=url)},
        "frame": None,
        "input_frame": None
    }
    full_queue = [open_url_slot] + queue_slots

    threading.Thread(target=execute_queue, args=(browser, full_queue), daemon=True).start()

def execute_queue(browser, queue):
    try:
        driver = get_driver(browser)
        while not stop_event.is_set():
            for slot in queue:
                if not slot['enabled_var'].get() or stop_event.is_set():
                    continue
                func_name = slot['func_var'].get()
                func = available_functions.get(func_name)
                args = [slot['inputs'][arg].get() for arg in function_args[func_name]]
                delay = int(slot['delay_var'].get()) if slot['delay_var'].get().isdigit() else 0
                time.sleep(delay)
                func(driver, *args)
            if execution_mode.get() == "close":
                break
        if execution_mode.get() == "close":
            driver.quit()
        messagebox.showinfo("Done", "Queue execution complete.")
    except Exception as e:
        messagebox.showerror("Execution Error", str(e))
    finally:
        run_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

def terminate_queue():
    stop_event.set()

def add_queue_slot():
    frame = tk.Frame(queue_container)
    frame.pack(fill=tk.X, pady=3)

    func_var = tk.StringVar(value=list(available_functions.keys())[0])
    dropdown = tk.OptionMenu(frame, func_var, *available_functions.keys(),
                              command=lambda _: update_inputs(func_var, input_frame, tooltip_btn))
    dropdown.pack(side=tk.LEFT, padx=5)

    tooltip_btn = tk.Label(frame, text="❓", fg="blue", cursor="question_arrow")
    tooltip_btn.pack(side=tk.LEFT)
    tooltip_btn.bind("<Enter>", lambda e: show_tooltip(tooltip_btn, function_docs[func_var.get()]))
    tooltip_btn.bind("<Leave>", lambda e: hide_tooltip(tooltip_btn))

    enabled_var = tk.BooleanVar(value=True)
    tk.Checkbutton(frame, text="Enable", variable=enabled_var).pack(side=tk.LEFT)

    tk.Label(frame, text="Delay (s):").pack(side=tk.LEFT)
    delay_var = tk.StringVar(value="0")
    tk.Entry(frame, textvariable=delay_var, width=4).pack(side=tk.LEFT)

    input_frame = tk.Frame(frame)
    input_frame.pack(side=tk.LEFT, padx=5)

    inputs = {}
    for arg in function_args[func_var.get()]:
        tk.Label(input_frame, text=f"{arg}:").pack(side=tk.LEFT)
        entry = tk.Entry(input_frame, width=10)
        entry.pack(side=tk.LEFT)
        inputs[arg] = entry

    def move_up():
        idx = queue_slots.index(slot)
        if idx > 0:
            queue_slots[idx], queue_slots[idx - 1] = queue_slots[idx - 1], queue_slots[idx]
            redraw_queue()

    def move_down():
        idx = queue_slots.index(slot)
        if idx < len(queue_slots) - 1:
            queue_slots[idx], queue_slots[idx + 1] = queue_slots[idx + 1], queue_slots[idx]
            redraw_queue()

    def remove():
        queue_slots.remove(slot)
        frame.destroy()

    tk.Button(frame, text="↑", command=move_up).pack(side=tk.LEFT)
    tk.Button(frame, text="↓", command=move_down).pack(side=tk.LEFT)
    tk.Button(frame, text="❌", command=remove).pack(side=tk.LEFT)

    slot = {
        "frame": frame,
        "func_var": func_var,
        "enabled_var": enabled_var,
        "delay_var": delay_var,
        "inputs": inputs,
        "input_frame": input_frame
    }
    queue_slots.append(slot)

def update_inputs(func_var, input_frame, tooltip_btn):
    for widget in input_frame.winfo_children():
        widget.destroy()
    slot = next(slot for slot in queue_slots if slot['func_var'] == func_var)
    slot['inputs'] = {}
    for arg in function_args[func_var.get()]:
        tk.Label(input_frame, text=f"{arg}:").pack(side=tk.LEFT)
        entry = tk.Entry(input_frame, width=10)
        entry.pack(side=tk.LEFT)
        slot['inputs'][arg] = entry
    tooltip_btn.bind("<Enter>", lambda e: show_tooltip(tooltip_btn, function_docs[func_var.get()]))

def redraw_queue():
    for widget in queue_container.winfo_children():
        widget.pack_forget()
    for slot in queue_slots:
        slot['frame'].pack(fill=tk.X, pady=3)

# --- Custom Queue Save/Load Setup ---
CUSTOM_FOLDER = os.path.join(os.path.dirname(__file__), "custom")
os.makedirs(CUSTOM_FOLDER, exist_ok=True)

# Ensure UI root is initialized before use
root = tk.Tk()
root.title("Selenium Function Queue Runner")
root.geometry("800x600")

mode_frame = tk.Frame(root)
mode_frame.pack(pady=5)
tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
mode = tk.StringVar(value="manual")
tk.Radiobutton(mode_frame, text="Manual", variable=mode, value="manual").pack(side=tk.LEFT)
tk.Radiobutton(mode_frame, text="Custom", variable=mode, value="custom").pack(side=tk.LEFT)

save_frame = tk.Frame(root)
save_frame.pack(pady=5)
tk.Label(save_frame, text="Custom Script Name:").pack(side=tk.LEFT)
save_name_entry = tk.Entry(save_frame, width=30)
save_name_entry.pack(side=tk.LEFT, padx=5)

def save_current_queue():
    name = save_name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter a name for the custom script.")
        return
    data = []
    for slot in queue_slots:
        data.append({
            "func": slot['func_var'].get(),
            "enabled": slot['enabled_var'].get(),
            "delay": slot['delay_var'].get(),
            "inputs": {k: v.get() for k, v in slot['inputs'].items()}
        })
    with open(os.path.join(CUSTOM_FOLDER, f"{name}.json"), 'w') as f:
        import json
        json.dump(data, f, indent=2)
    messagebox.showinfo("Saved", f"Custom script '{name}' saved.")

tk.Button(save_frame, text="💾 Save Queue", command=save_current_queue).pack(side=tk.LEFT)

# --- Custom Queue Dropdown Setup ---
custom_dropdown_var = tk.StringVar()
custom_dropdown = None

def load_custom_queue(*_):
    import json
    file = custom_dropdown_var.get()
    path = os.path.join(CUSTOM_FOLDER, file)
    if not os.path.isfile(path):
        messagebox.showerror("Error", f"Custom script '{file}' not found.")
        return
    with open(path, 'r') as f:
        data = json.load(f)
    for widget in queue_container.winfo_children():
        widget.destroy()
    queue_slots.clear()
    for entry in data:
        add_queue_slot()
        slot = queue_slots[-1]
        slot['func_var'].set(entry['func'])
        slot['enabled_var'].set(entry['enabled'])
        slot['delay_var'].set(entry['delay'])
        update_inputs(slot['func_var'], slot['input_frame'], None)
        for k, v in entry['inputs'].items():
            if k in slot['inputs']:
                slot['inputs'][k].delete(0, tk.END)
                slot['inputs'][k].insert(0, v)


def toggle_custom_dropdown(*_):
    global custom_dropdown
    if mode.get() == "custom":
        if custom_dropdown is None:
            dropdown_frame = tk.Frame(root)
            dropdown_frame.pack(pady=5)
            tk.Label(dropdown_frame, text="Load Custom Script:").pack(side=tk.LEFT)
            files = [f for f in os.listdir(CUSTOM_FOLDER) if f.endswith(".json")]
            if not files:
                files = ["<no scripts>"]
            custom_dropdown = tk.OptionMenu(dropdown_frame, custom_dropdown_var, *files, command=load_custom_queue)
            custom_dropdown.pack(side=tk.LEFT)
    elif custom_dropdown:
        custom_dropdown.destroy()
        custom_dropdown = None

mode.trace_add("write", toggle_custom_dropdown)

# --- UI Setup ---
# root setup moved earlier to prevent undefined errors

frame_browser = tk.Frame(root)
frame_browser.pack(pady=5)
tk.Label(frame_browser, text="Browser:").pack(side=tk.LEFT)
browser_choice = tk.StringVar(value="Chrome")
for b in ["Chrome", "Firefox", "Edge"]:
    tk.Radiobutton(frame_browser, text=b, variable=browser_choice, value=b).pack(side=tk.LEFT, padx=5)

frame_url = tk.Frame(root)
frame_url.pack(pady=5)
tk.Label(frame_url, text="URL:").pack(side=tk.LEFT)
url_input = tk.Entry(frame_url, width=60)
url_input.insert(0, "https://")
url_input.pack(side=tk.LEFT)

tk.Label(root, text="Function Queue:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10)
queue_container = tk.Frame(root)
queue_container.pack(fill=tk.X, padx=10)
tk.Button(root, text="+ Add Function to Queue", command=add_queue_slot).pack(pady=5)

frame_options = tk.Frame(root)
frame_options.pack(pady=5)
execution_mode = tk.StringVar(value="close")
tk.Label(frame_options, text="Execution Mode:", font=("Segoe UI", 10)).pack(anchor="w")
tk.Radiobutton(frame_options, text="Loop queue continuously", variable=execution_mode, value="loop").pack(anchor="w", padx=10)
tk.Radiobutton(frame_options, text="Close browser after completion", variable=execution_mode, value="close").pack(anchor="w", padx=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=15)
run_button = tk.Button(frame_buttons, text="▶ Execute Queue", width=20, command=run_queue)
run_button.pack(side=tk.LEFT, padx=10)
stop_button = tk.Button(frame_buttons, text="⛔ Terminate Queue", width=20, state=tk.DISABLED, command=terminate_queue)
stop_button.pack(side=tk.LEFT, padx=10)

root.mainloop()
