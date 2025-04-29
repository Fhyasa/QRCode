import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import io
import win32clipboard
from PIL import BmpImagePlugin

# Global variable to hold latest QR image
generated_qr_image = None

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
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Keep in memory
    generated_qr_image = qr_img

    # Resize for GUI display (fixed size, proportional)
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
        "URL: Enter a valid web address or any text you want to encode as a QR code.\n\n"
        "Size (box size): how many pixels wide each “box” of the QR code is.\n\n"
        "Border: number of boxes around the QR code.\n\n"
        "Larger size = higher resolution.\nMinimum border for most QR readers is 1."
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
border_entry.insert(0, "1")
border_entry.grid(row=1, column=1, padx=5)

generate_button = tk.Button(frame, text="Generate & Save QR Code", font=BUTTON_FONT, command=generate_qr)
generate_button.pack(pady=10, ipady=5)

preview_frame = tk.Frame(root, height=220, width=220)
preview_frame.pack(pady=10)
preview_frame.pack_propagate(False)

preview_label = tk.Label(preview_frame, text="QR Code Preview", font=("Helvetica", 12), fg="gray")
preview_label.pack()

copy_button = tk.Button(root, text="Copy QR to Clipboard", font=BUTTON_FONT, command=copy_to_clipboard)

url_entry.focus()

root.mainloop()