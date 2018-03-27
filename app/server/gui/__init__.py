import tkinter as tk
from PIL import Image, ImageTk

tk_root = tk.Tk()
tk_image_label = tk.Label(tk_root)
tk_image_label.pack()


def update_gui(map_image: Image):
    photo_image = ImageTk.PhotoImage(map_image)
    tk_image_label.configure(image=photo_image)
    tk_image_label.image = photo_image

    tk_root.update_idletasks()
    tk_root.update()
