import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import io
import win32clipboard
from PIL import BmpImagePlugin
from tkinter import colorchooser
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Global variable
generated_qr_image = None
settings_win = None
logo_path = None
use_logo = False
# Default Settings
fill_color = "black"
back_color = "white"
error_level = "H"
logo_position = "center"

def load_config():
    global fill_color, back_color, error_level, logo_path, use_logo, logo_position
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                fill_color = config.get("fill_color", "black")
                back_color = config.get("back_color", "white")
                error_level = config.get("error_level", "H")
                logo_path = config.get("logo_path", None)
                use_logo = config.get("use_logo", False)
                logo_position = config.get("logo_position", "center")
        except Exception as e:
            print("Failed to load config:", e)
load_config()

def generate_qr():
    global generated_qr_image

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    try:
        box_size = int(box_size_entry.get())
        border = int(border_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Box size and border must be integers.")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction={
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }[error_level],
        box_size=box_size,
        border=border
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

    # If logo is set, paste it into the center
    if use_logo and logo_path and os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Resize logo to fit 20% of QR width
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.2)
            logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

            # Determine position
            positions = {
                "center": ((qr_width - logo.width) // 2, (qr_height - logo.height) // 2),
                "top-left": (0, 0),
                "top-right": (qr_width - logo.width, 0),
                "bottom-left": (0, qr_height - logo.height),
                "bottom-right": (qr_width - logo.width, qr_height - logo.height),
            }
            xpos, ypos = positions.get(logo_position, positions["center"])

            qr_img.paste(logo, (xpos, ypos), logo)
        except Exception as e:
            messagebox.showwarning("Logo Error", f"Could not add logo:\n{e}")

    # Keep in memory
    generated_qr_image = qr_img

    # Resize for GUI display (fixed size, proportional)
    qr_display_img = qr_img.copy()
    qr_display_img.thumbnail((200, 200), Image.LANCZOS)
    qr_photo = ImageTk.PhotoImage(qr_display_img)

    preview_label.config(image=qr_photo, text="")
    preview_label.image = qr_photo

    if not copy_button.winfo_ismapped():
        copy_button.pack(pady=(0, 10), before=preview_frame)

    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
        title="Save QR Code As"
    )
    if save_path:
        generated_qr_image.save(save_path)
        messagebox.showinfo("Success", f"QR code saved to:\n{save_path}")

def copy_to_clipboard():
    if generated_qr_image is None:
        messagebox.showerror("Error", "No QR code generated yet.")
        return
    try:
        output = io.BytesIO()
        generated_qr_image.convert("RGB").save(output, "BMP")
        data = output.getvalue()
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data[14:])
        win32clipboard.CloseClipboard()

        messagebox.showinfo("Copied", "QR code image copied to clipboard.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy image:\n{e}")

def open_settings_window():
    global settings_win

    # If already open, bring it to front instead of opening a new one
    if settings_win and settings_win.winfo_exists():
        settings_win.lift()
        settings_win.focus_force()
        return

    settings_win = tk.Toplevel(root)
    settings_win.title("Advanced Settings")
    settings_win.resizable(False, False)
    settings_win.grab_set()
    settings_win.transient(root)

    sw = settings_win.winfo_screenwidth()
    sh = settings_win.winfo_screenheight()
    settings_win.geometry(f"+{int(sw/2 - 135)}+{int(sh/2 - 120)}")

    # Destroy reference on close
    def on_close():
        global settings_win
        if settings_win and settings_win.winfo_exists():
            settings_win.grab_release()
            settings_win.destroy()
        settings_win = None

    settings_win.protocol("WM_DELETE_WINDOW", on_close)

    # Color row frame
    color_frame = tk.Frame(settings_win)
    color_frame.pack(pady=(15, 5))

    fill_label = tk.Label(color_frame, text="Fill Color:", font=("Helvetica", 10))
    fill_label.grid(row=0, column=0, padx=5)
    fill_button = tk.Button(color_frame, width=10, bg=fill_color, command=lambda: choose_color('fill', fill_button))
    fill_button.grid(row=1, column=0, padx=5)

    back_label = tk.Label(color_frame, text="Background:", font=("Helvetica", 10))
    back_label.grid(row=0, column=1, padx=5)
    back_button = tk.Button(color_frame, width=10, bg=back_color, command=lambda: choose_color('back', back_button))
    back_button.grid(row=1, column=1, padx=5)

    # Error correction dropdown
    ec_frame = tk.Frame(settings_win)
    ec_frame.pack(pady=(10, 2))

    tk.Label(ec_frame, text="Error Correction:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")

    info_button = tk.Label(ec_frame, text="?", font=("Helvetica", 9, "bold"), fg="blue", cursor="question_arrow")
    info_button.grid(row=0, column=1, padx=(5, 0), sticky="w")

    def show_ec_info(event):
        messagebox.showinfo("Error Correction Levels", (
            "QR Code error correction levels:\n\n"
            "• L (Low) – Recovers ~7% data\n"
            "• M (Medium) – Recovers ~15% data\n"
            "• Q (Quartile) – Recovers ~25% data\n"
            "• H (High) – Recovers ~30% data\n\n"
            "Higher levels improve scannability with damage,\n"
            "but make the QR more dense (complex)."
        ))
        settings_win.lift()
        settings_win.focus_force()

    info_button.bind("<Button-1>", show_ec_info)

    ec_var = tk.StringVar(value=error_level)
    ec_menu = tk.OptionMenu(settings_win, ec_var, "L", "M", "Q", "H")
    ec_menu.config(width=5)
    ec_menu.pack()

    # Logo enable/disable checkbox
    logo_check_var = tk.BooleanVar(value=use_logo)
    logo_check = tk.Checkbutton(
        settings_win,
        text="Enable Logo",
        variable=logo_check_var,
        font=("Helvetica", 10)
    )
    logo_check.pack(pady=(5, 0))

    # Logo selector
    logo_frame = tk.Frame(settings_win)
    logo_frame.pack(pady=(5, 10))

    logo_label = tk.Label(logo_frame, text="Logo: ", font=("Helvetica", 10))
    logo_label.grid(row=0, column=0, padx=(0, 5))

    def open_logo_file(event):
        if logo_path and os.path.isfile(logo_path):
            try:
                os.startfile(logo_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showinfo("Logo", "No logo file selected.")

    logo_filename = os.path.basename(logo_path) if logo_path else "None selected"
    logo_name_var = tk.StringVar()
    logo_name_display = tk.Label(logo_frame, textvariable=logo_name_var, font=("Helvetica", 9))
    logo_name_display.grid(row=0, column=1)

    def update_logo_display():
        if logo_path:
            logo_name_var.set(os.path.basename(logo_path))
            logo_name_display.config(
                fg="blue",
                cursor="hand2",
                font=("Helvetica", 9, "underline")
            )
            logo_name_display.bind("<Button-1>", open_logo_file)
        else:
            logo_name_var.set("None selected")
            logo_name_display.config(
                fg="black",
                cursor="arrow",
                font=("Helvetica", 9)
            )
            logo_name_display.unbind("<Button-1>")

    def choose_logo():
        global logo_path
        path = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            logo_path = path
            update_logo_display()
        
    def remove_logo():
        global logo_path
        logo_path = None
        update_logo_display()

    logo_buttons_frame = tk.Frame(settings_win)
    logo_buttons_frame.pack()

    logo_button = tk.Button(logo_buttons_frame, text="Choose Logo", font=("Helvetica", 10), command=choose_logo)
    logo_button.grid(row=0, column=0, padx=5)

    remove_logo_button = tk.Button(logo_buttons_frame, text="Remove Logo", font=("Helvetica", 10), command=remove_logo)
    remove_logo_button.grid(row=0, column=1, padx=5)

    # Logo position dropdown
    tk.Label(settings_win, text="Logo Position:", font=("Helvetica", 10)).pack(pady=(8, 0))
    logo_pos_var = tk.StringVar(value=logo_position)
    pos_menu = tk.OptionMenu(settings_win, logo_pos_var, "center", "top-left", "top-right", "bottom-left", "bottom-right")
    pos_menu.config(width=12)
    pos_menu.pack()

    def save_and_close():
        global error_level, logo_path, use_logo, logo_position, settings_win
        error_level = ec_var.get()
        use_logo = logo_check_var.get()
        logo_position = logo_pos_var.get()
        save_config()
        if settings_win and settings_win.winfo_exists():
            settings_win.grab_release()
            settings_win.destroy()
        settings_win = None

    save_button = tk.Button(settings_win, text="Save Settings", font=("Helvetica", 10, "bold"), command=save_and_close)
    save_button.pack(pady=15)

    update_logo_display()

def choose_color(which, button):
    global fill_color, back_color
    initial = fill_color if which == 'fill' else back_color
    color = colorchooser.askcolor(title="Choose Color", initialcolor=initial)
    if color[1]:
        if which == 'fill':
            fill_color = color[1]
        else:
            back_color = color[1]
        button.config(bg=color[1])

def save_config():
    config = {
        "fill_color": fill_color,
        "back_color": back_color,
        "error_level": error_level,
        "use_logo": use_logo,
        "logo_position": logo_position
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", "Settings saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings:\n{e}")

# Setup GUI
root = tk.Tk()
root.title("QR Code Generator")
root.geometry("400x600")
root.resizable(False, False)

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

LABEL_FONT = ("Helvetica", 14)
BUTTON_FONT = ("Helvetica", 12, "bold")

frame = tk.Frame(root, padx=20, pady=20, relief="groove", borderwidth=2)
frame.pack(pady=20, fill="x")

# Info button in top right corner of frame
info_button = tk.Label(frame, text="?", font=("Helvetica", 10, "bold"), fg="blue", cursor="question_arrow")
info_button.place(relx=1.0, x=-10, y=5, anchor="ne")

def show_info(event):
    messagebox.showinfo(
        "Info",
        "A QR code Generator made by Aske\n\n"
        "URL: Enter a valid web address or any text you want to encode as a QR code.\n\n"
        "Size (box size): how many pixels wide each “box” of the QR code is.\n\n"
        "Border: number of boxes around the QR code.\n\n"
        "A larger size results in higher resolution.\n"
        "The minimum border required by most QR readers is 1.\nA border of 4 is recommended."
    )

info_button.bind("<Button-1>", show_info)

title_label = tk.Label(frame, text="Enter URL to Generate QR", font=LABEL_FONT)
title_label.pack(pady=10)

url_entry = tk.Entry(frame, font=("Helvetica", 12), width=40)
url_entry.pack(pady=10)

# Settings row centered
settings_row = tk.Frame(frame)
settings_row.pack(pady=(5, 10))

box_size_label = tk.Label(settings_row, text="Size", font=("Helvetica", 10))
box_size_label.grid(row=0, column=0, padx=5)
box_size_entry = tk.Entry(settings_row, font=("Helvetica", 10), width=10)
box_size_entry.insert(0, "40")
box_size_entry.grid(row=1, column=0, padx=5)

border_label = tk.Label(settings_row, text="Border", font=("Helvetica", 10))
border_label.grid(row=0, column=1, padx=5)
border_entry = tk.Entry(settings_row, font=("Helvetica", 10), width=10)
border_entry.insert(0, "4")
border_entry.grid(row=1, column=1, padx=5)

settings_button = tk.Button(frame, text="Settings", font=BUTTON_FONT, command=open_settings_window)
settings_button.pack(pady=5, ipady=2)

generate_button = tk.Button(frame, text="Generate & Save QR Code", font=BUTTON_FONT, command=generate_qr)
generate_button.pack(pady=10, ipady=5)

# Frame to hold both copy button and preview
preview_container = tk.Frame(root)
preview_container.pack(pady=10)

copy_button = tk.Button(preview_container, text="Copy QR to Clipboard", font=BUTTON_FONT, command=copy_to_clipboard)

preview_frame = tk.Frame(preview_container, height=220, width=220)
preview_frame.pack()
preview_frame.pack_propagate(False)

preview_label = tk.Label(preview_frame, text="QR Code Preview", font=("Helvetica", 12), fg="gray")
preview_label.pack()

url_entry.focus()

root.mainloop()