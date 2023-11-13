import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import asdict

from .Contracts.abstractview import AbstractView
from .Datas.viewsettings import ViewSettings


class View(AbstractView):
    def setup_ui(self, view_settings: ViewSettings, controller) -> None:
        self._view_settings = view_settings
        self._controller = controller

        self._setup_root()
        self._setup_frame()

    def _setup_root(self):
        self._root = tk.Tk()

        width, height = 600, 200
        posx = (self._root.winfo_screenwidth() - width) // 2
        posy = (self._root.winfo_screenheight() - height) // 2
        self._root.geometry(f'{width}x{height}+{posx}+{posy}')

        self._root.title('Software Updater Tool')

        self._root.resizable(False, False)
        self._root.protocol('WM_DELETE_WINDOW', self.close_window_event)

    def _setup_frame(self):
        frame = tk.Frame(self._root, bg=self._view_settings.bg)
        frame.pack(fill=tk.BOTH, expand=True)

        self.header_var = tk.StringVar()

        tk.Label(
            frame,
            cnf=asdict(self._view_settings),
            textvariable=self.header_var,
        ).pack(fill=tk.X, expand=True, padx=10, pady=(10, 0))

        self.var_progress_bar = tk.DoubleVar(value=0.0)

        self._progress_bar = ttk.Progressbar(
            frame,
            mode='determinate',
            variable=self.var_progress_bar,
        )
        self._progress_bar.pack(fill=tk.X, expand=True, padx=10, pady=(10, 0))

        self.main_var = tk.StringVar()
        tk.Label(
            frame,
            cnf=asdict(self._view_settings),
            textvariable=self.main_var,
        ).pack(fill=tk.X, expand=True, padx=10, pady=(10, 0))

        self.footer_var = tk.StringVar()
        tk.Label(
            frame,
            cnf=asdict(self._view_settings),
            textvariable=self.footer_var,
        ).pack(fill=tk.X, expand=True, padx=10, pady=(10, 0))

    def config_progress_bar(self, content_length: int) -> None:
        self._progress_bar.configure(maximum=content_length)

    def update_progress_bar(self, value: float) -> None:
        self.var_progress_bar.set(value)

    def loop(self) -> None:
        self._root.mainloop()

    def set_title(self, string: str) -> None:
        self.header_var.set(string)

    def set_main(self, string: str) -> None:
        self.main_var.set(string)

    def set_footer(self, string: str) -> None:
        self.footer_var.set(string)

    def close_window_event(self) -> None:
        self._controller.close_window_event()
