import calendar
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import font, messagebox, simpledialog

# PAZIŅOJUMI(uzlabot, jo šis variants neatļauj uzstādīt laiku)
try:
    from win10toast import ToastNotifier
except ImportError:
    ToastNotifier = None

# PASĀKUMI
EVENTS = {}

# TŪLKOJUMS
TEXT = {
    "lv": {"title": "Kalendārs", "language": "Valoda", "theme": "Motīvs",
           "add": "Pievienot pasākumu", "enter": "Ievadi pasākumu datumam",
           "empty": "Pasākuma apraksts nevar būt tukšs.", "warning": "Brīdinājums",
           "black": "Melns motīvs", "white": "Balts motīvs",
           "today": "Šodien ir plānoti notikumi:", "year": "Ievadi gadu:"},
    "en": {"title": "Calendar", "language": "Language", "theme": "Theme",
           "add": "Add event", "enter": "Enter an event for",
           "empty": "Event description cannot be empty.", "warning": "Warning",
           "black": "Black theme", "white": "White theme",
           "today": "Events planned for today:", "year": "Enter year:"},
    "ru": {"title": "Календарь", "language": "Язык", "theme": "Тема",
           "add": "Добавить событие", "enter": "Введите событие для",
           "empty": "Описание события не может быть пустым.", "warning": "Предупреждение",
           "black": "Черная тема", "white": "Белая тема",
           "today": "Сегодня запланированы события:", "year": "Введите год:"},
}

# NEDĒĻAS DIENAS TŪLKOJUMS
WEEKDAYS = {
    "lv": ["P", "O", "T", "C", "P", "S", "Sv"],
    "en": ["M", "T", "W", "T", "F", "S", "S"],
    "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
}

# MĒNEŠU TŪLKOJUMS
MONTHS = {
    "lv": ["", "Janvāris", "Februāris", "Marts", "Aprīlis", "Maijs", "Jūnijs",
           "Jūlijs", "Augusts", "Septembris", "Oktobris", "Novembris", "Decembris"],
    "en": ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "ru": ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
}

# KRĀSAS
THEMES = {
    "white": {"bg": "#f3f3f3", "cell": "#ffffff", "event": "#fff7c2",
              "selected": "#ffd900", "text": "#1a1a1a"},
    "black": {"bg": "#1d1d1d", "cell": "#2a2a2a", "event": "#3a3a3a",
              "selected": "#525E6D", "text": "#f0f0f0"},
}

# PAMATIZMĒRS
BASE_W, BASE_H = 900, 600
LINE = 3  # STANDARTA LĪNIJU BIEZUMS


class CalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "lv"                # VALODA
        self.theme = "white"            # MOTĪVS
        self.current = date.today()     # DATUMS
        self.last_reminder = None       # ATGĀDINĀJUMS
        self.radios = []                # POGAS
        self.icon_size = 16             # IKONAS IZM.

        # FONTI(izmērs atkarīgs)
        self.small_font = font.Font(family="Arial", size=11)
        self.bold_font = font.Font(family="Arial", weight="bold", size=12)
        self.big_font = font.Font(family="Arial", weight="bold", size=14)
        self.week_font = font.Font(family="Arial", weight="bold", size=-18)
        self.day_font = font.Font(family="Arial", weight="bold", size=-24)
        self.note_font = font.Font(family="Arial", size=-10)

        # LOGS
        self.geometry(f"{BASE_W}x{BASE_H}")
        self.minsize(700, 500)

        # STARTS
        self.build()
        self.refresh()
        self.tick()
        self.remind()

        # TAUSTIŅI
        self.bind("<Left>", lambda e: self.move_day(-1))
        self.bind("<Right>", lambda e: self.move_day(1))
        self.bind("<Up>", lambda e: self.move_month(1))
        self.bind("<Down>", lambda e: self.move_month(-1))
        self.bind("<Configure>", self.resize)

    def tr(self, key):
        # Tulkojums
        return TEXT[self.lang][key]


    def build(self):
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=12, pady=12)

        # SĀNJOSLA
        self.side = tk.Frame(main, width=170, bd=LINE, relief="solid")
        self.side.pack(side="left", fill="y", padx=(0, 12))
        self.side.pack_propagate(False)  # Fiksēts platums

        # VALODAS
        self.lang_label = tk.Label(self.side, font=self.bold_font)
        self.lang_label.pack(anchor="w", padx=14, pady=(16, 8))
        self.lang_var = tk.StringVar(value="lv")
        for code, name in (("lv", "Latviešu"), ("en", "English"), ("ru", "Русский")):
            self.radio(self.side, name, self.lang_var, code,
                       self.change_language).pack(anchor="w", padx=14, pady=3)

        # MOTĪVS
        theme_box = tk.Frame(self.side, bd=LINE, relief="solid")
        theme_box.pack(fill="x", padx=9, pady=15)
        self.theme_label = tk.Label(theme_box, font=self.bold_font)
        self.theme_label.pack(anchor="w", padx=8, pady=(10, 5))
        self.theme_var = tk.StringVar(value="white")
        self.theme_buttons = {}
        for value in ("black", "white"):
            button = self.radio(theme_box, "", self.theme_var, value, self.change_theme)
            button.pack(anchor="w", padx=8, pady=3)
            self.theme_buttons[value] = button

        # LAIKS
        self.clock = tk.Label(self.side, font=self.bold_font)
        self.clock.pack(side="bottom", anchor="w", padx=14, pady=8)


        area = tk.Frame(main)
        area.pack(side="left", fill="both", expand=True)


        # DATUMS
        bar = tk.Frame(area)
        bar.pack(fill="x", pady=(0, 8))
        nav = dict(width=3, font=self.small_font, bd=LINE, relief="solid")  # Pogu stils
        tk.Button(bar, text="←", command=lambda: self.move_day(-1), **nav).pack(side="left")

        
        date_box = tk.Frame(bar, bd=LINE, relief="solid")
        date_box.pack(side="left", padx=8)
        self.month_label = tk.Label(date_box, font=self.big_font)
        self.month_label.pack(side="left", padx=8)
        self.year_label = tk.Label(date_box, font=self.big_font, cursor="hand2")
        self.year_label.pack(side="left", padx=5)
        self.year_label.bind("<Button-1>", self.edit_year)

        tk.Button(bar, text="→", command=lambda: self.move_day(1), **nav).pack(side="left", padx=(0, 10))
        tk.Button(bar, text="▲", command=lambda: self.move_month(1), **nav).pack(side="left")
        tk.Button(bar, text="▼", command=lambda: self.move_month(-1), **nav).pack(side="left", padx=(4, 0))

        # DIENAS
        self.days_frame = tk.Frame(area)
        self.days_frame.pack(fill="both", expand=True)
        self.days_frame.bind("<Configure>", self.resize_days)
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1, uniform="col")  
        for i in range(1, 7):
            self.days_frame.grid_rowconfigure(i, weight=1, uniform="row")   

    # LOGU IZMĒRS
    def resize(self, event):
        if event.widget is not self:
            return
        scale = max(1, min(event.width / BASE_W, event.height / BASE_H, 2.5))
        self.small_font.config(size=int(11 * scale))
        self.bold_font.config(size=int(12 * scale))
        self.big_font.config(size=int(14 * scale))
        self.side.config(width=int(170 * scale))
        size = int(16 * scale)  
        if size != self.icon_size:
            self.icon_size = size
            self.set_icons(THEMES[self.theme])

    def resize_days(self, event):
        size = min(event.width, event.height) / 7
        self.week_font.config(size=-max(16, int(size * 0.28)))
        self.day_font.config(size=-max(18, int(size * 0.35)))
        self.note_font.config(size=-max(10, int(size * 0.13)))

    def paint(self, widget, c):
        kind = widget.winfo_class()
        if kind in ("Tk", "Frame"):
            widget.config(bg=c["bg"])
        elif kind == "Label":
            widget.config(bg=c["bg"], fg=c["text"])
        elif kind in ("Button", "Radiobutton"):
            widget.config(bg=c["bg"], fg=c["text"], activebackground=c["bg"])
            if kind == "Radiobutton":
                widget.config(selectcolor=c["bg"])
        for child in widget.winfo_children():
            self.paint(child, c)  

    # APAĻĀS POGAS
    def radio(self, parent, text, variable, value, command):
        button = tk.Radiobutton(parent, text=text, font=self.small_font, variable=variable,
                                value=value, command=command, indicatoron=False,
                                compound="left", bd=0, highlightthickness=0, padx=4)
        self.radios.append(button)
        return button

    def circle(self, c, selected):
        size = self.icon_size
        r = size / 2
        img = tk.PhotoImage(width=size, height=size)
        for y in range(size):
            row = []
            for x in range(size):
                d = ((x + 0.5 - r) ** 2 + (y + 0.5 - r) ** 2) ** 0.5  
                if r - max(2, size // 8) < d <= r or (selected and d <= r * 0.5):
                    row.append(c["text"]) 
                else:
                    row.append(c["bg"])   
            img.put("{" + " ".join(row) + "}", to=(0, y))
        return img

    # IKONU MAIŅA
    def set_icons(self, c):
        self.icons = (self.circle(c, False), self.circle(c, True)) 
        for button in self.radios:
            button.config(image=self.icons[0], selectimage=self.icons[1])

    # VALODAS MAIŅA
    def change_language(self):
        self.lang = self.lang_var.get()
        self.refresh()

    # MOTĪVA MAIŅA
    def change_theme(self):
        self.theme = self.theme_var.get()
        self.refresh()

    # UPDATE
    def refresh(self):
        c = THEMES[self.theme]

        # TEKSTI
        self.title(self.tr("title"))
        self.lang_label.config(text=self.tr("language"))
        self.theme_label.config(text=self.tr("theme"))
        for value, button in self.theme_buttons.items():
            button.config(text=self.tr(value))
        self.month_label.config(text=MONTHS[self.lang][self.current.month])
        self.year_label.config(text=str(self.current.year))

        # KRĀSAS
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        self.paint(self, c)
        self.set_icons(c)
        self.draw_days(c)

    # DIENAS
    def draw_days(self, c):
        # Nedēļas dienas
        for col, name in enumerate(WEEKDAYS[self.lang]):
            tk.Label(self.days_frame, text=name, font=self.week_font,
                     relief="solid", borderwidth=LINE, bg=c["cell"], fg=c["text"]
                     ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        year, month = self.current.year, self.current.month
        first, days = calendar.monthrange(year, month)

        for day in range(1, days + 1):
            events = EVENTS.get(date(year, month, day), [])

            
            if day == self.current.day:
                bg = c["selected"]
            else:
                bg = c["event"] if events else c["cell"]

            
            row, col = divmod(first + day - 1, 7) 
            cell = tk.Frame(self.days_frame, bg=bg, relief="solid", borderwidth=LINE)
            cell.grid(row=row + 1, column=col, sticky="nsew", padx=1, pady=1)
            cell.pack_propagate(False)

            
            number = tk.Label(cell, text=day, font=self.day_font, bg=bg, fg=c["text"])
            number.pack(anchor="nw", padx=4)

            
            preview = "\n".join(e[:12] + ("..." if len(e) > 12 else "") for e in events[:2])
            note = tk.Label(cell, text=preview, font=self.note_font, justify="left",
                            bg=bg, fg=c["text"])
            note.pack(anchor="nw", padx=4)

            
            for part in (cell, number, note):
                part.bind("<Button-1>", lambda e, d=day: self.add_event(d))

    # PASĀKUMI // EVENTS
    def add_event(self, day):
        selected = date(self.current.year, self.current.month, day)
        text = simpledialog.askstring(
            self.tr("add"), f"{self.tr('enter')} {selected:%Y-%m-%d}:")
        if text is None:  # Atcelts
            return
        if not text.strip():
            messagebox.showwarning(self.tr("warning"), self.tr("empty"))
            return

        EVENTS.setdefault(selected, []).append(text.strip())
        self.current = selected
        self.refresh()
        if selected == date.today():
            self.remind()

    # DIENAS MAIŅA
    def move_day(self, amount):
        self.current += timedelta(days=amount)
        self.refresh()

    # MĒNEŠA MAIŅA
    def move_month(self, amount):
        month = self.current.month - 1 + amount
        self.set_date(self.current.year + month // 12, month % 12 + 1)

    # GADA MAIŅA
    def edit_year(self, event=None):
        year = simpledialog.askinteger(self.tr("title"), self.tr("year"),
                                       initialvalue=self.current.year,
                                       minvalue=1, maxvalue=9999)
        if year:
            self.set_date(year, self.current.month)

    # DATUMA IZVĒLE
    def set_date(self, year, month):
        day = min(self.current.day, calendar.monthrange(year, month)[1])
        self.current = date(year, month, day)
        self.refresh()

    # PULKSTENIS
    def tick(self):
        self.clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.tick)

    # ATGĀDINĀJUS
    def remind(self):
        today = date.today()
        events = EVENTS.get(today, [])
        if not events or self.last_reminder == today:
            return
        message = self.tr("today") + "\n\n" + "\n".join("- " + e for e in events)
        try:
            ToastNotifier().show_toast(self.tr("title"), message, duration=10)
        except Exception:
            print(message) 
        self.last_reminder = today

    # IZVEIDO UN NOTUR KALENDĀRA LOGU ATVĒRTU
if __name__ == "__main__":
    CalendarApp().mainloop()


"""


    ⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀ ⣀⣀⣤⣤⣤⣀⡀
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠸⣼⡿
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇
⠀⠀ ⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠇
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃


"""
