import time
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir
from typing import Callable, Optional
from urllib.parse import quote
from zipfile import ZipFile, is_zipfile

from requests import Response, exceptions, get

from .Contracts.abstractmodel import AbstractModel
from .Datas.viewsettings import ViewSettings


class Model(AbstractModel):
    def __init__(self):
        self.base_url = 'https://www.efscode.com.br/atualizacoes/downloads/'

    def get_view_settings(self) -> ViewSettings:
        self.view_settings = ViewSettings()
        return self.view_settings

    def mount_url(self, software_name: str) -> str:
        return quote(f'{self.base_url}{software_name}.zip', safe=':/')

    def stabilish_connection(self, url: str) -> Response:
        try:
            connection = get(url, stream=True, timeout=500)
            if connection.status_code != 200:
                raise ConnectionError('Não foi possível se conectar ao servidor')
            return connection
        except exceptions.ConnectionError:
            raise ConnectionError('Não foi possível se conectar ao servidor')

    def download(
        self,
        connection: Response,
        content_length: int,
        destination: NamedTemporaryFile,
        update_progress_bar_cmd: Callable[[int], None],
        set_main_cmd: Callable[[str], None],
    ) -> None:
        str_content_length = self.bytes_to_human_readable(content_length)
        total_downloaded = 0
        init_time = time.time()
        for data in connection.iter_content(chunk_size=4096):
            destination.write(data)

            total_downloaded += len(data)
            update_progress_bar_cmd(total_downloaded)

            str_total_downloaded = self.bytes_to_human_readable(total_downloaded)
            str_download_speed = self._calculate_download_speed(
                total_downloaded, init_time
            )

            set_main_cmd(
                f'{str_total_downloaded}/{str_content_length} - {str_download_speed} '
            )

    def tmp_new_version_file_path(self, software_name: str) -> NamedTemporaryFile:
        return NamedTemporaryFile(
            prefix=f'{software_name}_new_', suffix='.zip', delete=False
        )

    @lru_cache(maxsize=20)
    def bytes_to_human_readable(self, byte_size: int) -> str:
        units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        i = 0
        while byte_size >= 1024 and i < len(units) - 1:
            byte_size /= 1024
            i += 1
        return f'{byte_size:.2f} {units[i]}'

    def _calculate_download_speed(self, downloaded_size: int, init_time: float) -> str:
        tempo_decorrido = time.time() - init_time
        if not tempo_decorrido:
            return
        velocidade = downloaded_size / tempo_decorrido
        return f'Velocidade: {self.bytes_to_human_readable(int(velocidade))}/s'

    def check_integrity(self, temp_file: NamedTemporaryFile) -> bool:
        return is_zipfile(temp_file)

    def extract_data(self, temp_file: NamedTemporaryFile) -> None:
        zip_file = ZipFile(temp_file, 'r', allowZip64=False)
        zip_file.extractall('./')
