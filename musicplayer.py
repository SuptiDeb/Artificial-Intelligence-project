
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class MusicPlayerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("700x450")
        self.root.minsize(480, 320)

        # Theme colors
        self.bg_overlay = "#0f1724"   # dark slate for overlay
        self.card_bg = "#111827"
        self.accent = "#10b981"  # teal/green accent
        self.btn_bg = "#1f2937"
        self.btn_hover = "#334155"
        self.text_fg = "#E6EEF3"

        # Load background image path
        img_path = "music-with-euqalizer.jpg"

        # create a canvas that fills the window to hold the background
        self.bg_canvas = Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Try load image; if not present use solid color
        self.original_image = None
        if os.path.exists(img_path):
            try:
                self.original_image = Image.open(img_path).convert("RGBA")
                # initial fill
                self._update_background_image(self.root.winfo_width() or 700, self.root.winfo_height() or 450)
            except Exception as e:
                messagebox.showwarning("Image load error", f"Could not open background image:\n{e}\nUsing solid background.")
                self.bg_canvas.configure(bg="#0b1220")
        else:
            # fallback solid color background
            self.bg_canvas.configure(bg="#0b1220")

        # overlay frame (to place controls) - visually a centered card
        self.card = Frame(self.root, bg=self.card_bg, bd=0, relief=FLAT)
        # Use place with relative coords to center and provide responsiveness
        self.card.place(relx=0.5, rely=0.5, anchor=CENTER, width=520, height=320)

        # Title
        self.title_label = Label(self.card, text="🎵 My Music Player", font=("Segoe UI", 18, "bold"),
                                 bg=self.card_bg, fg=self.text_fg)
        self.title_label.place(x=20, y=16)

        # Song display (big)
        self.song_label = Label(self.card, text="No song selected", font=("Segoe UI", 12),
                                bg=self.card_bg, fg="#cfe8df")
        self.song_label.place(x=20, y=60)

        # Icon (visual)
        self.icon_label = Label(self.card, text="🎧", font=("Segoe UI", 36),
                                bg=self.card_bg, fg=self.accent)
        self.icon_label.place(relx=1.0, x=-80, y=30, anchor=NE)

        # Progress bar (ttk)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#0b1220",
                        background=self.accent, bordercolor=self.card_bg, lightcolor=self.accent, darkcolor=self.accent)
        self.progress_var = DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(self.card, style="Green.Horizontal.TProgressbar",
                                        orient="horizontal", mode="determinate",
                                        variable=self.progress_var, maximum=100)
        self.progress.place(x=20, y=120, width=480, height=12)

        # Time labels
        self.time_current = Label(self.card, text="0:00", bg=self.card_bg, fg="#9aa9a3", font=("Segoe UI", 10))
        self.time_current.place(x=20, y=140)
        self.time_total = Label(self.card, text="3:30", bg=self.card_bg, fg="#9aa9a3", font=("Segoe UI", 10))
        self.time_total.place(x=470, y=140, anchor=NE)

        # Control buttons area
        btn_y = 180
        btn_w = 80
        btn_h = 42
        self.play_btn = Button(self.card, text="▶", font=("Segoe UI", 14, "bold"),
                               bg=self.btn_bg, fg=self.text_fg, bd=0, activebackground=self.btn_hover,
                               command=self.play)
        self.play_btn.place(x=120, y=btn_y, width=btn_w, height=btn_h)
        self._add_hover(self.play_btn)

        self.pause_btn = Button(self.card, text="⏸", font=("Segoe UI", 14),
                                bg=self.btn_bg, fg=self.text_fg, bd=0, activebackground=self.btn_hover,
                                command=self.pause)
        self.pause_btn.place(x=220, y=btn_y, width=btn_w, height=btn_h)
        self._add_hover(self.pause_btn)

        self.stop_btn = Button(self.card, text="⏹", font=("Segoe UI", 14),
                               bg=self.btn_bg, fg=self.text_fg, bd=0, activebackground=self.btn_hover,
                               command=self.stop)
        self.stop_btn.place(x=320, y=btn_y, width=btn_w, height=btn_h)
        self._add_hover(self.stop_btn)

        # Volume slider
        vol_label = Label(self.card, text="Volume", bg=self.card_bg, fg="#9aa9a3", font=("Segoe UI", 10))
        vol_label.place(x=20, y=240)
        self.volume = ttk.Scale(self.card, from_=0, to=100, orient="horizontal")
        self.volume.set(70)
        self.volume.place(x=80, y=236, width=200)

        # Playlist area (simple listbox)
        pl_label = Label(self.card, text="Playlist", bg=self.card_bg, fg="#9aa9a3", font=("Segoe UI", 10))
        pl_label.place(x=300, y=160)
        self.playlist = Listbox(self.card, bg="#0b1220", fg="#d5e9e0", bd=0, highlightthickness=0,
                                selectbackground="#164e44", font=("Segoe UI", 10))
        # add some demo items
        for i, title in enumerate(["Demo Song 1", "Demo Song 2", "Demo Song 3", "Demo Song 4"], start=1):
            self.playlist.insert(END, f"{i}. {title}")
        self.playlist.place(x=300, y=184, width=200, height=90)

        # internal state
        self._is_playing = False
        self._progress_percent = 0.0

        # Bind resize to update background image
        self.root.bind("<Configure>", self._on_root_resize)

    # ---------- Background helpers ----------
    def _update_background_image(self, width, height):
        """Resize original image to width x height and put on canvas."""
        if not self.original_image:
            return
        try:
            resized = self.original_image.resize((max(1, width), max(1, height)), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized, master=self.root)
            # put image on canvas
            self.bg_canvas.delete("bgimg")
            self.bg_canvas.create_image(0, 0, anchor=NW, image=self.bg_photo, tags="bgimg")
            # keep references so GC doesn't remove it
            self.bg_canvas.image = self.bg_photo
            self.root._bg_photo = self.bg_photo
        except Exception as e:
            # fail silently (canvas bg color stays)
            print("Background update error:", e)

    def _on_root_resize(self, event):
        # Update background image to new window size (debounce small events)
        # event.width/height may be tiny during startup; use after to delay slightly
        if self.original_image:
            # use after_cancel + after technique to avoid many resizes
            try:
                if hasattr(self, "_resize_after_id"):
                    self.root.after_cancel(self._resize_after_id)
            except Exception:
                pass
            self._resize_after_id = self.root.after(120, lambda: self._update_background_image(self.root.winfo_width(), self.root.winfo_height()))

    # ---------- Button behaviors ----------
    def _add_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.configure(bg=self.btn_hover))
        widget.bind("<Leave>", lambda e: widget.configure(bg=self.btn_bg))

    def play(self):
        if not self._is_playing:
            self._is_playing = True
            self.song_label.config(text="Demo Song playing...")
            self._animate_progress()

    def pause(self):
        if self._is_playing:
            self._is_playing = False
            self.song_label.config(text="Paused")

    def stop(self):
        self._is_playing = False
        self._progress_percent = 0.0
        self.progress_var.set(0.0)
        self.song_label.config(text="Stopped / No song selected")

    def _animate_progress(self):
        if not self._is_playing:
            return
        # increment
        self._progress_percent += 0.8  # control speed
        if self._progress_percent >= 100:
            self._progress_percent = 100
            self._is_playing = False
            self.song_label.config(text="Finished")
        self.progress_var.set(self._progress_percent)
        # update current time label roughly (for demo)
        total_seconds = 3*60 + 30  # 3:30 demo
        cur = int(total_seconds * (self._progress_percent / 100.0))
        m = cur // 60
        s = cur % 60
        self.time_current.config(text=f"{m}:{s:02d}")
        if self._is_playing:
            self.root.after(150, self._animate_progress)

# Run the app
if __name__ == "__main__":
    # Save as a .py and run with `python filename.py` for best results (Tkinter inside Jupyter can be flaky).
    root = Tk()
    app = MusicPlayerUI(root)
    root.mainloop()
