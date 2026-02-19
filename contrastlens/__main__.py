import tkinter as tk

from contrastlens.ui import ContrastLensUI


def main():
    root = tk.Tk()
    ContrastLensUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
