
# Vienkāršs kalendāra ģenerators
# Izdrukā mēneša kalendāru dotajam gadam un mēnesim

from datetime import date, datetime
import os
import tkinter as tk
import webbrowser
from tkinter import simpledialog, messagebox

# Šī vārdnīca glabā pasākumus pēc datuma: (gads, mēnesis, diena) -> [apraksti].
# Piemērs: EVENTS[(2025, 5, 12)] = ["Ārsta vizīte", "Zvanīt mammai"]
EVENTS = {}


# Izveido teksta kalendāru vienam mēnesim.
# Šī funkcija atgriež virkni, kas izskatās kā standarta kalendāra izkārtojums.
def generate_calendar(year: int, month: int) -> str:
    """Atgriež teksta kalendāru dotajam gadam un mēnesim."""
    # Pārbauda mēneša numuru, lai nepieļautu neiespējamās vērtības.
    if not 1 <= month <= 12:
        raise ValueError("Mēnesim jābūt no 1 līdz 12.")

    # date(year, month, 1) norāda izvēlētā mēneša pirmo dienu.
    first_day = date(year, month, 1)

    # Saskaita, cik dienas ir izvēlētajā mēnesī.
    days_in_month = 31
    if month == 2:
        days_in_month = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
    elif month in (4, 6, 9, 11):
        days_in_month = 30

    # weekday() atgriež 0 pirmdienai un 6 svētdienai.
    weekday = first_day.weekday()
    month_name = first_day.strftime("%B")

    # Veido kalendāra rindas pa rindām.
    lines = [f"{month_name} {year}", "Po Tu We Th Fr Se Sv"]
    week = ["  " for _ in range(weekday)]

    # Pievieno katra mēneša dienas skaita atbilstošās vērtības nedēļas sarakstā.
    for day in range(1, days_in_month + 1):
        week.append(f"{day:2d}")
        if len(week) == 7:
            lines.append(" ".join(week))
            week = []

    # Ja pēdējā nedēļa nav pilna, aizpilda atlikušās vietas ar tukšām šūnām.
    if week:
        while len(week) < 7:
            week.append("  ")
        lines.append(" ".join(week))

    return "\n".join(lines)


# Pievieno jaunu pasākumu noteiktai dienai.
# Ja datums jau pastāv vārdnīcā, pievieno vēl vienu pasākumu tam datumam.
def set_event(year: int, month: int, day: int, description: str) -> None:
    """Pievieno pasākumu noteiktai datumam."""
    # Pamata validācija, lai izvairītos no nederīgiem datumiem vai tukšiem aprakstiem.
    if not 1 <= month <= 12:
        raise ValueError("Mēnesim jābūt no 1 līdz 12.")
    if not 1 <= day <= 31:
        raise ValueError("Dienai jābūt no 1 līdz 31.")

    if not description or not description.strip():
        raise ValueError("Pasākuma apraksts nevar būt tukšs.")

    event_key = (year, month, day)
    EVENTS.setdefault(event_key, []).append(description.strip())


# Atgriež visus pasākumus izvēlētai dienai.
# Ja pasākumu nav, funkcija atgriež tukšu sarakstu.
def get_events_for_day(year: int, month: int, day: int):
    """Atgriež pasākumu sarakstu izvēlētajam datumam."""
    return EVENTS.get((year, month, day), [])


# Galvenais kalendāra lietotnes logs.
# Tas ir tkinter.Tk apakšklase, kas izveido reālo GUI logu.
class CalendarApp(tk.Tk):
    TEXT = {
        "lv": {
            "app_title": "Kalendārs",
            "language": "Valoda",
            "theme": "Motīvs",
            "select_language": "Izvēlies valodu",
            "select_theme": "Izvēlies krāsu motīvu",
            "prev": "<<",
            "next": ">>",
            "warning": "Brīdinājums",
            "empty_event": "Pasākuma apraksts nevar būt tukšs.",
            "add_event": "Pievienot pasākumu",
            "enter_event": "Ievadi pasākumu datumam",
            "month": "Mēnesis",
            "day": "Diena",
            "latvian": "Latviešu",
            "english": "English",
            "russian": "Русский",
            "black_theme": "Melns motīvs",
            "white_theme": "Balts motīvs",
        },
        "en": {
            "app_title": "Calendar",
            "language": "Language",
            "theme": "Theme",
            "select_language": "Choose a language",
            "select_theme": "Choose a color theme",
            "prev": "<<",
            "next": ">>",
            "warning": "Warning",
            "empty_event": "Event description cannot be empty.",
            "add_event": "Add event",
            "enter_event": "Enter an event for",
            "month": "Month",
            "day": "Day",
            "latvian": "Latviešu",
            "english": "English",
            "russian": "Русский",
            "black_theme": "Black theme",
            "white_theme": "White theme",
        },
        "ru": {
            "app_title": "Календарь",
            "language": "Язык",
            "theme": "Тема",
            "select_language": "Выберите язык",
            "select_theme": "Выберите цветовую тему",
            "prev": "<<",
            "next": ">>",
            "warning": "Предупреждение",
            "empty_event": "Описание события не может быть пустым.",
            "add_event": "Добавить событие",
            "enter_event": "Введите событие для",
            "month": "Месяц",
            "day": "День",
            "latvian": "Latviešu",
            "english": "English",
            "russian": "Русский",
            "black_theme": "Черная тема",
            "white_theme": "Белая тема",
        },
    }

    WEEKDAYS = {
        "lv": ["P", "O", "T", "C", "P", "S", "Sv"],
        "en": ["M", "T", "W", "T", "F", "S", "S"],
        "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    }

    MONTH_NAMES = {
        "lv": ["", "Janvāris", "Februāris", "Marts", "Aprīlis", "Maijs", "Jūnijs", "Jūlijs", "Augusts", "Septembris", "Oktobris", "Novembris", "Decembris"],
        "en": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        "ru": ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
    }

    def __init__(self):
        # Izsauc vecāku Tk klases inicializāciju un iestata pamata lietotnes parametrus.
        super().__init__()
        self.language = "lv"
        self.theme = "white"
        self.title(self.t("app_title"))
        self.geometry("900x600")
        self.minsize(700, 500)

        # Iestata pašreizējo gadu un mēnesi, kā arī atmiņas mainīgos, kas palīdz darboties ar ievadi.
        self.current_year = date.today().year
        self.current_month = date.today().month
        self.pending_day_input = ""
        self.day_buttons = {}

        # Izveido galveno satvara rāmi un kreiso izvēlnes paneli.
        self.main_frame = tk.Frame(self, bg="#f3f3f3")
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.lang_panel = tk.Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid")
        self.lang_panel.pack(side="left", fill="y", padx=(0, 12))

        # Izveido valodas izvēles etiķeti un radio pogas.
        self.lang_label = tk.Label(self.lang_panel, text=self.t("language"), font=("Arial", 12, "bold"))
        self.lang_label.pack(anchor="w", padx=16, pady=(16, 8))

        self.language_var = tk.StringVar(value="lv")
        for code, label in (("lv", self.t("latvian")), ("en", self.t("english")), ("ru", self.t("russian"))):
            radio = tk.Radiobutton(
                self.lang_panel,
                text=label,
                variable=self.language_var,
                value=code,
                command=self.change_language,
                font=("Arial", 11),
                indicatoron=True,
            )
            radio.pack(anchor="w", padx=16, pady=4)

        # Izveido tēmas izvēles paneli.
        self.theme_panel = tk.Frame(self.lang_panel, bg="#f4f4f4", bd=1, relief="solid")
        self.theme_panel.pack(fill="x", padx=10, pady=(12, 16))

        self.theme_label = tk.Label(self.theme_panel, text=self.t("theme"), font=("Arial", 12, "bold"))
        self.theme_label.pack(anchor="w", padx=16, pady=(16, 8))

        self.theme_var = tk.StringVar(value="white")
        for value, label in (("black", self.t("black_theme")), ("white", self.t("white_theme"))):
            theme_radio = tk.Radiobutton(
                self.theme_panel,
                text=label,
                variable=self.theme_var,
                value=value,
                command=self.change_theme,
                font=("Arial", 11),
                indicatoron=True,
            )
            theme_radio.pack(anchor="w", padx=16, pady=4)

        # Izveido pulksteņa etiķeti, kas parāda pašreizējo laiku.
        self.clock_label = tk.Label(
            self.lang_panel,
            text="",
            font=("Arial", 12, "bold"),
            anchor="w",
            bd=0,
        )
        self.clock_label.pack(side="bottom", fill="x", padx=16, pady=(0, 0))

        # Izveido saitīti uz kalendāra HTML failu apakšējā kreisajā stūrī.
        self.kalendar_link_label = tk.Label(
            self.lang_panel,
            text="kalendar.html",
            font=("Arial", 10, "underline"),
            anchor="w",
            bd=0,
            cursor="hand2",
        )
        self.kalendar_link_label.pack(side="bottom", fill="x", padx=16, pady=(0, 16))
        self.kalendar_link_label.bind("<Button-1>", self.open_kalendar_html)

        # Izveido kalendāra apgabalu un augšējo joslu ar navigācijas pogām.
        self.calendar_area = tk.Frame(self.main_frame, bg="#f3f3f3")
        self.calendar_area.pack(side="left", fill="both", expand=True)

        self.top_bar = tk.Frame(self.calendar_area, bg="#f3f3f3")
        self.top_bar.pack(fill="x", pady=(0, 8))

        self.prev_btn = tk.Button(self.top_bar, text=self.t("prev"), command=self.prev_month, width=4)
        self.prev_btn.pack(side="left")

        self.month_label = tk.Label(self.top_bar, text="", font=("Arial", 14, "bold"), bg="#f3f3f3")
        self.month_label.pack(side="left")

        self.year_label = tk.Label(self.top_bar, text="", font=("Arial", 14, "bold"), bg="#f3f3f3", cursor="hand2")
        self.year_label.pack(side="left", padx=(10, 0))
        self.year_label.bind("<Button-1>", self.start_year_edit)

        self.next_btn = tk.Button(self.top_bar, text=self.t("next"), command=self.next_month, width=4)
        self.next_btn.pack(side="left", padx=(10, 0))

        self.calendar_frame = tk.Frame(self.calendar_area, bg="#f3f3f3")
        self.calendar_frame.pack(fill="both", expand=True)

        # Saista tastatūras īsinājumus ar kalendāra navigāciju un ievadi.
        self.bind("<Left>", self.on_left_arrow)
        self.bind("<Right>", self.on_right_arrow)
        self.bind("<Key>", self.on_key_press)

        # Inicializē pulksteni, tēmu un kalendāru.
        self.update_clock()
        self.apply_theme()
        self.render_month()

    def t(self, key: str) -> str:
        return self.TEXT.get(self.language, self.TEXT["lv"]).get(key, key)

    def month_name(self, year: int, month: int) -> str:
        return self.MONTH_NAMES[self.language][month]

    def weekday_names(self):
        return self.WEEKDAYS[self.language]

    def change_language(self):
        self.language = self.language_var.get()
        self.title(self.t("app_title"))
        self.prev_btn.config(text=self.t("prev"))
        self.next_btn.config(text=self.t("next"))
        self.lang_label.config(text=self.t("language"))
        self.theme_label.config(text=self.t("theme"))
        for child in self.theme_panel.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(text=self.t("black_theme") if child.cget("value") == "black" else self.t("white_theme"))
        self.render_month()

    def change_theme(self):
        self.theme = self.theme_var.get()
        self.apply_theme()
        self.render_month()

    def apply_theme(self):
        if self.theme == "black":
            bg_window = "#111111"
            bg_panel = "#1d1d1d"
            bg_area = "#181818"
            bg_cell = "#2a2a2a"
            bg_cell_event = "#3a3a3a"
            fg_main = "#f0f0f0"
            fg_muted = "#d0d0d0"
            fg_day = "#ffffff"
            border = "#3a3a3a"
        else:
            bg_window = "#f3f3f3"
            bg_panel = "#ffffff"
            bg_area = "#f3f3f3"
            bg_cell = "white"
            bg_cell_event = "#FFF7C2"
            fg_main = "#1a1a1a"
            fg_muted = "#333333"
            fg_day = "#000000"
            border = "#d0d0d0"

        self.configure(bg=bg_window)
        self.main_frame.config(bg=bg_window)
        self.lang_panel.config(bg=bg_panel)
        self.theme_panel.config(bg=bg_panel)

        self.lang_label.config(bg=bg_panel, fg=fg_main)
        self.theme_label.config(bg=bg_panel, fg=fg_main)
        self.month_label.config(bg=bg_area, fg=fg_main)
        self.year_label.config(bg=bg_area, fg=fg_main)
        self.calendar_area.config(bg=bg_area)
        self.top_bar.config(bg=bg_area)
        self.calendar_frame.config(bg=bg_area)

        for widget in self.lang_panel.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.config(bg=bg_panel, fg=fg_main, selectcolor=bg_panel)
        for widget in self.theme_panel.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.config(bg=bg_panel, fg=fg_main, selectcolor=bg_panel)

        self.prev_btn.config(bg=bg_panel, fg=fg_main, activebackground=bg_panel, activeforeground=fg_main)
        self.next_btn.config(bg=bg_panel, fg=fg_main, activebackground=bg_panel, activeforeground=fg_main)
        self.clock_label.config(bg=bg_panel, fg=fg_main)
        self.kalendar_link_label.config(
            bg=bg_panel,
            fg="#1a73e8" if self.theme == "white" else "#7cc0ff",
            activeforeground="#1a73e8" if self.theme == "white" else "#7cc0ff",
        )

        for widget in self.calendar_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=bg_cell, fg=fg_main, relief="solid", borderwidth=1)
            elif isinstance(widget, tk.Button):
                widget.config(bg=bg_cell_event if get_events_for_day(self.current_year, self.current_month, int(widget.cget("text").splitlines()[0])) else bg_cell,
                             fg=fg_day,
                             activebackground=bg_cell_event if get_events_for_day(self.current_year, self.current_month, int(widget.cget("text").splitlines()[0])) else bg_cell,
                             activeforeground=fg_day)

    def update_clock(self):
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def open_kalendar_html(self, event=None):
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kalendar.html")
        if os.path.exists(html_path):
            webbrowser.open_new_tab(f"file://{html_path}")
        else:
            messagebox.showwarning("Warning", "kalendar.html fails netika atrasts.")

    def on_left_arrow(self, event=None):
        self.prev_month()
        return "break"

    def on_right_arrow(self, event=None):
        self.next_month()
        return "break"

    def on_key_press(self, event=None):
        if event is None:
            return

        # Don't hijack typing in the year entry while the user is editing the year.
        if isinstance(event.widget, (tk.Entry, tk.Text)):
            return

        if event.char is None or not event.char.isdigit():
            return

        self.pending_day_input += event.char
        max_day = self._days_in_current_month()
        candidate = int(self.pending_day_input)

        if 1 <= candidate <= max_day:
            self.add_event(candidate)
            self.pending_day_input = ""
            return "break"

        if candidate > max_day or len(self.pending_day_input) > 2:
            self.pending_day_input = ""
            return "break"

        return "break"

    def start_year_edit(self, event=None):
        if getattr(self, "_year_editing", False):
            return

        self._year_editing = True
        self.year_label.pack_forget()

        self.year_entry = tk.Entry(
            self.top_bar,
            width=6,
            font=("Arial", 14, "bold"),
            justify="center",
            relief="solid",
            bd=1,
        )
        self.year_entry.insert(0, str(self.current_year))
        self.year_entry.select_range(0, tk.END)
        self.year_entry.pack(side="left", padx=(10, 0))
        self.year_entry.focus_set()
        self.year_entry.bind("<Return>", self.commit_year_edit)
        self.year_entry.bind("<FocusOut>", self.commit_year_edit)

    def commit_year_edit(self, event=None):
        if not hasattr(self, "year_entry") or self.year_entry is None:
            return

        raw_value = self.year_entry.get().strip()
        self.year_entry.destroy()
        self.year_entry = None
        self._year_editing = False

        if raw_value and raw_value.isdigit():
            new_year = int(raw_value)
            if new_year >= 1:
                self.current_year = new_year
                self.pending_day_input = ""
                self.render_month()
                return

        self.render_month()

    def _days_in_current_month(self):
        if self.current_month == 2:
            return 29 if (self.current_year % 4 == 0 and (self.current_year % 100 != 0 or self.current_year % 400 == 0)) else 28
        if self.current_month in (4, 6, 9, 11):
            return 30
        return 31

    def prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.pending_day_input = ""
        self.render_month()

    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.pending_day_input = ""
        self.render_month()

    def _day_button_text(self, day: int) -> str:
        events = get_events_for_day(self.current_year, self.current_month, day)
        if not events:
            return str(day)

        preview = []
        for event in events[:2]:
            cleaned = event.strip()
            if not cleaned:
                continue
            preview.append(cleaned[:12] + ("..." if len(cleaned) > 12 else ""))

        if not preview:
            return str(day)

        return f"{day}\n" + "\n".join(preview)

    def render_month(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(text=self.month_name(self.current_year, self.current_month))
        self.year_label.config(text=str(self.current_year))

        if not getattr(self, "_year_editing", False):
            if self.year_label.winfo_ismapped():
                pass
            else:
                self.year_label.pack(side="left", padx=(10, 0), before=self.next_btn)

        for index, day_name in enumerate(self.weekday_names()):
            label = tk.Label(self.calendar_frame, text=day_name, font=("Arial", 10, "bold"), width=12, relief="solid")
            label.grid(row=0, column=index, sticky="nsew", padx=1, pady=1)

        first_day = date(self.current_year, self.current_month, 1)
        first_weekday = first_day.weekday()
        days_in_month = self._days_in_current_month()

        row = 1
        col = first_weekday

        for day in range(1, days_in_month + 1):
            events = get_events_for_day(self.current_year, self.current_month, day)
            btn = tk.Button(
                self.calendar_frame,
                text=self._day_button_text(day),
                width=12,
                height=3,
                anchor="n",
                justify="left",
                command=lambda d=day: self.add_event(d),
                relief="ridge",
                bg="#FFF7C2" if events else "white",
                fg="black",
                font=("Arial", 8),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            self.day_buttons[(row, col)] = btn
            col += 1
            if col > 6:
                col = 0
                row += 1

        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(1, row + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1)

        self.apply_theme()

    def add_event(self, day: int):
        event_title = self.t("add_event")
        event_text = f"{self.t('enter_event')} {date(self.current_year, self.current_month, day).strftime('%Y-%m-%d')}:"
        description = simpledialog.askstring(event_title, event_text)
        if description is None:
            return
        description = description.strip()
        if not description:
            messagebox.showwarning(self.t("warning"), self.t("empty_event"))
            return

        set_event(self.current_year, self.current_month, day, description)
        self.render_month()


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
