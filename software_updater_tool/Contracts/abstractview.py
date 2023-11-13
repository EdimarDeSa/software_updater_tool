from abc import ABC, abstractmethod

from ..Datas.viewsettings import ViewSettings


class AbstractView(ABC):
    @abstractmethod
    def setup_ui(self, view_settings: ViewSettings, controller) -> None:
        pass

    @abstractmethod
    def config_progress_bar(self, content_length: int) -> None:
        pass

    @abstractmethod
    def update_progress_bar(self, value: float) -> None:
        pass

    @abstractmethod
    def loop(self) -> None:
        pass

    @abstractmethod
    def set_title(self, string: str) -> None:
        pass

    @abstractmethod
    def set_main(self, string: str) -> None:
        pass

    @abstractmethod
    def set_footer(self, string: str) -> None:
        pass
