import json
import random
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk

DATA1 = ["C", "A", "G"]
DATA2 = [1, 2, 3, 4, 5, 6]
STATE_FILE = Path(".last_pair.json")


def load_prev_pair():
    try:
        if STATE_FILE.exists():
            with STATE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                prev = tuple(data.get("pair", []))
                if len(prev) == 2:
                    return prev
    except Exception:
        pass
    return None


def save_pair(pair):
    try:
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"pair": list(pair)}, f)
    except Exception:
        pass


def pick_pair(prev):
    # retry-until-different
    a = random.choice(DATA1)
    b = random.choice(DATA2)
    cur = (a, b)
    if prev is None:
        return cur
    while cur == prev:
        a = random.choice(DATA1)
        b = random.choice(DATA2)
        cur = (a, b)
    return cur


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fretboard Learning")
        self.geometry("560x360")
        self.minsize(460, 300)

        # layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        for r in range(5):
            container.rowconfigure(r, weight=1)

        # fonts
        self.header_font = ("Segoe UI", 16, "bold")
        self.result_font = ("Consolas", 18)
        self.small_font = ("Segoe UI", 10)

        # ----- header with stopwatch -----
        self.start_time = None
        self.stopwatch_running = False
        self.header_var = tk.StringVar(value="Random Pair Generator — 00:00:00")
        self.header_label = ttk.Label(container, textvariable=self.header_var, font=self.header_font, anchor="center")
        self.header_label.grid(row=0, column=0, sticky="n", pady=(0, 8))

        # ----- result -----
        self.result_var = tk.StringVar(value="Note: –, String: –")
        self.result_label = ttk.Label(container, textvariable=self.result_var, font=self.result_font, anchor="center")
        self.result_label.grid(row=1, column=0, sticky="n", pady=(0, 16))

        # ----- big button -----
        self.generate_btn = ttk.Button(container, text="Generate Pair", command=self.on_generate)
        self.generate_btn.grid(row=2, column=0, sticky="", pady=8, ipadx=24, ipady=12)

        # hint
        hint = ttk.Label(container, text="Tip: Press Space or Enter", font=self.small_font, foreground="#666")
        hint.grid(row=3, column=0, sticky="n", pady=(4, 0))

        # status bar
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(container, textvariable=self.status_var, font=self.small_font, foreground="#666")
        status.grid(row=4, column=0, sticky="s")

        # load prev pair (still used internally, just not shown)
        self.prev_pair = load_prev_pair()

        # keybindings
        self.bind("<space>", lambda e: self.on_generate())
        self.bind("<Return>", lambda e: self.on_generate())

        # style
        try:
            self.style = ttk.Style(self)
            if "vista" in self.style.theme_names():
                self.style.theme_use("vista")
            elif "clam" in self.style.theme_names():
                self.style.theme_use("clam")
            self.style.configure("TButton", font=("Segoe UI", 12))
        except Exception:
            pass

    # format stopwatch
    @staticmethod
    def format_hms(sec):
        sec = int(sec)
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_stopwatch(self):
        if not self.stopwatch_running or self.start_time is None:
            return
        elapsed = time.monotonic() - self.start_time
        self.header_var.set(f"Random Pair Generator — {self.format_hms(elapsed)}")
        self.after(1000, self.update_stopwatch)

    def on_generate(self):
        # start stopwatch on FIRST click only
        if not self.stopwatch_running:
            self.start_time = time.monotonic()
            self.stopwatch_running = True
            self.update_stopwatch()

        pair = pick_pair(self.prev_pair)
        self.result_var.set(f"Note: {pair[0]}, String: {pair[1]}")
        self.status_var.set("Generated a new pair.")
        save_pair(pair)
        self.prev_pair = pair


if __name__ == "__main__":
    App().mainloop()