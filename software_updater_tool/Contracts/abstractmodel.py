from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
from typing import Callable

from requests import Response

from ..Datas.viewsettings import ViewSettings


class AbstractModel(ABC):
    @abstractmethod
    def get_view_settings(self) -> ViewSettings:
        pass

    @abstractmethod
    def mount_url(self, software_name: str) -> str:
        pass

    @abstractmethod
    def stabilish_connection(self, url: str) -> Response:
        pass

    @abstractmethod
    def bytes_to_human_readable(self, byte_size: int) -> str:
        pass

    @abstractmethod
    def download(
        self,
        connection: Response,
        content_length: int,
        destination: NamedTemporaryFile,
        update_progress_bar_cmd: Callable[[int], None],
        set_main_cmd: Callable[[str], None],
    ) -> None:
        pass

    @abstractmethod
    def tmp_new_version_file_path(self, software_name: str) -> NamedTemporaryFile:
        pass

    @abstractmethod
    def check_integrity(self, temp_file: NamedTemporaryFile) -> bool:
        pass

    @abstractmethod
    def extract_data(self, temp_file: NamedTemporaryFile) -> None:
        pass
