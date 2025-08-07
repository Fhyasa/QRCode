import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import io
import win32clipboard
from tkinter import colorchooser
import os
import json

from Library.settings import open_settings_window as settings_window

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Global variables
generated_qr_image = None
logo_path = None
use_logo = False
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

def save_config():
    config = {
        "fill_color": fill_color,
        "back_color": back_color,
        "error_level": error_level,
        "use_logo": use_logo,
        "logo_position": logo_position,
        "logo_path": logo_path
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        messagebox.showinfo("Saved", "Settings saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings:\n{e}")

def open_settings_window():
    def save_config_callback(new_error_level, new_use_logo, new_logo_position, new_logo_path, new_fill_color, new_back_color):
        global error_level, use_logo, logo_position, logo_path, fill_color, back_color
        error_level = new_error_level
        use_logo = new_use_logo
        logo_position = new_logo_position
        logo_path = new_logo_path
        fill_color = new_fill_color
        back_color = new_back_color
        save_config()

    settings_window(
        root=root,
        fill_color=fill_color,
        back_color=back_color,
        error_level=error_level,
        logo_path=logo_path,
        use_logo=use_logo,
        logo_position=logo_position,
        save_config_callback=save_config_callback
    )

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

    if use_logo and logo_path and os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.2)
            logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

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

    generated_qr_image = qr_img
    qr_display_img = qr_img.copy()
    qr_display_img.thumbnail((200, 200), Image.LANCZOS)
    qr_photo = ImageTk.PhotoImage(qr_display_img)

    preview_label.config(image=qr_photo, text="")
    preview_label.image = qr_photo

    if not copy_button.winfo_ismapped():
        copy_button.pack(pady=10)

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

# GUI setup
root = tk.Tk()
root.title("QR Code Generator")
root.geometry("400x600")
root.resizable(False, False)

root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
root.geometry(f"+{x}+{y}")

LABEL_FONT = ("Helvetica", 14)
BUTTON_FONT = ("Helvetica", 12, "bold")

frame = tk.Frame(root, padx=20, pady=20, relief="groove", borderwidth=2)
frame.pack(pady=20, fill="x")

info_button = tk.Label(frame, text="?", font=("Helvetica", 10, "bold"), fg="blue", cursor="question_arrow")
info_button.place(relx=1.0, x=-10, y=5, anchor="ne")
info_button.bind("<Button-1>", lambda e: messagebox.showinfo(
    "Info",
    "A QR code Generator made by Aske\n\n"
    "URL: Enter a valid web address or any text you want to encode as a QR code.\n\n"
    "Size (box size): how many pixels wide each “box” of the QR code is.\n\n"
    "Border: number of boxes around the QR code.\n\n"
    "A larger size results in higher resolution.\n"
    "The minimum border required by most QR readers is 1.\nA border of 4 is recommended."
))

tk.Label(frame, text="Enter URL to Generate QR", font=LABEL_FONT).pack(pady=10)

url_entry = tk.Entry(frame, font=("Helvetica", 12), width=40)
url_entry.pack(pady=10)

settings_row = tk.Frame(frame)
settings_row.pack(pady=(5, 10))

tk.Label(settings_row, text="Size", font=("Helvetica", 10)).grid(row=0, column=0, padx=5)
box_size_entry = tk.Entry(settings_row, font=("Helvetica", 10), width=10)
box_size_entry.insert(0, "40")
box_size_entry.grid(row=1, column=0, padx=5)

tk.Label(settings_row, text="Border", font=("Helvetica", 10)).grid(row=0, column=1, padx=5)
border_entry = tk.Entry(settings_row, font=("Helvetica", 10), width=10)
border_entry.insert(0, "4")
border_entry.grid(row=1, column=1, padx=5)

tk.Button(frame, text="Settings", font=BUTTON_FONT, command=open_settings_window).pack(pady=5, ipady=2)
tk.Button(frame, text="Generate & Save QR Code", font=BUTTON_FONT, command=generate_qr).pack(pady=10, ipady=5)

preview_frame = tk.Frame(root, height=220, width=220)
preview_frame.pack(pady=10)
preview_frame.pack_propagate(False)

preview_label = tk.Label(preview_frame, text="QR Code Preview", font=("Helvetica", 12), fg="gray")
preview_label.pack()

copy_button = tk.Button(root, text="Copy QR to Clipboard", font=BUTTON_FONT, command=copy_to_clipboard)

url_entry.focus()
root.mainloop()