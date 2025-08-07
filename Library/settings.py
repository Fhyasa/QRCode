import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os

def open_settings_window(
    root,
    fill_color,
    back_color,
    error_level,
    logo_path,
    use_logo,
    logo_position,
    save_config_callback
):
    settings_win = tk.Toplevel(root)
    settings_win.title("Advanced Settings")
    settings_win.resizable(False, False)
    #settings_win.geometry("300x310")
    settings_win.grab_set()
    settings_win.transient(root)

    sw = settings_win.winfo_screenwidth()
    sh = settings_win.winfo_screenheight()
    settings_win.geometry(f"+{int(sw/2 - 135)}+{int(sh/2 - 120)}")

    def on_close():
        settings_win.grab_release()
        settings_win.destroy()

    settings_win.protocol("WM_DELETE_WINDOW", on_close)

    # --- Internal state updates ---
    current_fill_color = fill_color
    current_back_color = back_color
    current_logo_path = logo_path

    # Choose color
    def choose_color(which, button):
        nonlocal current_fill_color, current_back_color
        initial = current_fill_color if which == 'fill' else current_back_color
        color = colorchooser.askcolor(title="Choose Color", initialcolor=initial)
        if color[1]:
            if which == 'fill':
                current_fill_color = color[1]
            else:
                current_back_color = color[1]
            button.config(bg=color[1])

    # Color row
    color_frame = tk.Frame(settings_win)
    color_frame.pack(pady=(15, 5))

    tk.Label(color_frame, text="Fill Color:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5)
    fill_button = tk.Button(color_frame, width=10, bg=current_fill_color, command=lambda: choose_color('fill', fill_button))
    fill_button.grid(row=1, column=0, padx=5)

    tk.Label(color_frame, text="Background:", font=("Helvetica", 10)).grid(row=0, column=1, padx=5)
    back_button = tk.Button(color_frame, width=10, bg=current_back_color, command=lambda: choose_color('back', back_button))
    back_button.grid(row=1, column=1, padx=5)

    # Error correction
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
        ), parent=settings_win)
        settings_win.grab_set()
        settings_win.lift()
        settings_win.focus_force()

    info_button.bind("<Button-1>", show_ec_info)

    ec_var = tk.StringVar(value=error_level)
    ec_menu = tk.OptionMenu(settings_win, ec_var, "L", "M", "Q", "H")
    ec_menu.config(width=5)
    ec_menu.pack()

    # Logo enable checkbox
    logo_check_var = tk.BooleanVar(value=use_logo)
    logo_check = tk.Checkbutton(
        settings_win,
        text="Enable Logo",
        variable=logo_check_var,
        font=("Helvetica", 10)
    )
    logo_check.pack(pady=(5, 0))

    # Logo file section
    logo_frame = tk.Frame(settings_win)
    logo_frame.pack(pady=(5, 10))

    tk.Label(logo_frame, text="Logo: ", font=("Helvetica", 10)).grid(row=0, column=0, padx=(0, 5))
    logo_name_var = tk.StringVar()
    logo_name_display = tk.Label(logo_frame, textvariable=logo_name_var, font=("Helvetica", 9))
    logo_name_display.grid(row=0, column=1)

    def update_logo_display():
        if current_logo_path:
            logo_name_var.set(os.path.basename(current_logo_path))
            logo_name_display.config(
                fg="blue",
                cursor="hand2",
                font=("Helvetica", 9, "underline")
            )
            logo_name_display.bind("<Button-1>", lambda e: os.startfile(current_logo_path))
        else:
            logo_name_var.set("None selected")
            logo_name_display.config(fg="black", cursor="arrow", font=("Helvetica", 9))
            logo_name_display.unbind("<Button-1>")

    def choose_logo():
        nonlocal current_logo_path
        path = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            current_logo_path = path
            update_logo_display()

    def remove_logo():
        nonlocal current_logo_path
        current_logo_path = None
        update_logo_display()

    logo_buttons_frame = tk.Frame(settings_win)
    logo_buttons_frame.pack()

    tk.Button(logo_buttons_frame, text="Choose Logo", font=("Helvetica", 10), command=choose_logo).grid(row=0, column=0, padx=5)
    tk.Button(logo_buttons_frame, text="Remove Logo", font=("Helvetica", 10), command=remove_logo).grid(row=0, column=1, padx=5)

    # Logo position
    tk.Label(settings_win, text="Logo Position:", font=("Helvetica", 10)).pack(pady=(8, 0))
    logo_pos_var = tk.StringVar(value=logo_position)
    pos_menu = tk.OptionMenu(settings_win, logo_pos_var, "center", "top-left", "top-right", "bottom-left", "bottom-right")
    pos_menu.config(width=12)
    pos_menu.pack()

    def save_and_close():
        save_config_callback(
            ec_var.get(),
            logo_check_var.get(),
            logo_pos_var.get(),
            current_logo_path,
            current_fill_color,
            current_back_color
        )
        on_close()

    tk.Button(settings_win, text="Save Settings", font=("Helvetica", 10, "bold"), command=save_and_close).pack(pady=15)

    update_logo_display()