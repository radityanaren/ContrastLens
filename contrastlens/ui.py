# ui.py

import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from contrastlens.processor import ContrastLens


class ContrastLensUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ContrastLens")
        self.root.geometry("1000x750")

        self.original_image = None
        self.current_result = None
        self.showing_original = False

        self.contrast_value = tk.DoubleVar(value=0.5)
        self.mode = tk.StringVar(value="low")

        self._build_ui()

    def _build_ui(self):
        control_frame = tk.Frame(self.root, pady=12)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(
            control_frame, text="Load Image", width=12, command=self.load_image
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            control_frame, text="Save Image", width=12, command=self.save_image
        ).pack(side=tk.LEFT, padx=8)

        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=20)

        tk.Radiobutton(
            mode_frame,
            text="Low Contrast",
            variable=self.mode,
            value="low",
            command=self.update_preview,
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            mode_frame,
            text="High Contrast",
            variable=self.mode,
            value="high",
            command=self.update_preview,
        ).pack(side=tk.LEFT)

        slider_frame = tk.Frame(control_frame)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)

        tk.Label(slider_frame, text="Contrast").pack(side=tk.LEFT)

        self.slider = tk.Scale(
            slider_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.contrast_value,
            showvalue=False,
            command=lambda _: self.update_preview(),
        )
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.canvas = tk.Canvas(self.root, bg="#eeeeee")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-1>", self._show_original)
        self.canvas.bind("<ButtonRelease-1>", self._show_processed)

        self.status = tk.Label(
            self.root, text="Load an image to begin", font=("Arial", 9), fg="gray"
        )
        self.status.pack(side=tk.BOTTOM, pady=6)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return

        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Failed to load image")
            return

        self.original_image = img
        self.status.config(text="Image loaded")
        self.update_preview()

    def update_preview(self):
        if self.original_image is None:
            return

        self.current_result = ContrastLens.process(
            image=self.original_image,
            contrast=self.contrast_value.get(),
            mode=self.mode.get(),
        )

        if not self.showing_original:
            self._display_image(self.current_result)

    def save_image(self):
        if self.current_result is None:
            messagebox.showwarning("Warning", "Nothing to save")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG", "*.png")]
        )
        if not path:
            return

        cv2.imwrite(path, self.current_result)
        self.status.config(text="Image saved")

    def _display_image(self, image):
        self.canvas.delete("all")

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return

        if image.ndim == 2:
            h, w = image.shape
            img_rgb = image
        else:
            h, w = image.shape[:2]
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        scale = min(canvas_w / w, canvas_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

        pil = Image.fromarray(resized)
        self.tk_image = ImageTk.PhotoImage(pil)

        self.canvas.create_image(
            canvas_w // 2, canvas_h // 2, image=self.tk_image, anchor=tk.CENTER
        )

    def _show_original(self, event):
        if self.original_image is None:
            return
        self.showing_original = True
        self._display_image(self.original_image)
        self.status.config(text="Showing original (release to return)")

    def _show_processed(self, event):
        self.showing_original = False
        if self.current_result is not None:
            self._display_image(self.current_result)
        self.status.config(text="Processed preview")

    def _on_resize(self, event):
        if self.showing_original and self.original_image is not None:
            self._display_image(self.original_image)
        elif self.current_result is not None:
            self._display_image(self.current_result)
