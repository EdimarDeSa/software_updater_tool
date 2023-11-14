import os
import re
import signal
import subprocess
from pathlib import Path
from tempfile import gettempdir

import requests.exceptions

from .Contracts.abstractmodel import AbstractModel
from .Contracts.abstractview import AbstractView
from .WorkersBrewery import WorkersBrewery


class DownloadError(Exception):
    ...


#     def gera_bkp(self):
#         self.bak_path = temp.mktemp(prefix=f'{self.nome_do_software}_bak_')
#         self.atualiza_informacao('Criando backup.')
#         try:
#             shutil.make_archive(self.bak_path, 'zip', self.pasta_software)
#         except Exception as e:
#             self.atualiza_informacao(f'Falha/n{e}/nao criar backup.')
#             # Lidar com o erro adequadamente
#         self.bak_path += '.zip'
#         self.atualiza_informacao('Backup criado com sucesso.')
#


class Controller:
    def __init__(self, view: AbstractView, model: AbstractModel, software_name: str):
        self._view = view
        self._model = model

        self.local = Path(__file__).resolve().parent.parent

        self._brewery = WorkersBrewery(2, wait_time=1, daemon_workers=True)

        self.software_name = software_name

        self._pid = os.getpid()

    def start(self):
        view_settings = self._model.get_view_settings()
        self._view.setup_ui(view_settings, self)

    def mainloop(self):
        self._view.loop()

    def start_update_process(self) -> None:
        self._brewery.hire_a_worker('update_process', self._update_process, {})

    def _update_process(self) -> None:
        try:
            self._view.set_title('Iniciando atualização')

            # self.bkp_file_path = self._model.bkp_file_path()

            url = self._model.mount_url(self.software_name)
            self._view.set_main(f'Connectando ao servidor.../n{url}')
            connection = self._model.stabilish_connection(url)

            content_length = int(connection.headers.get('content-length', 0))
            self._view.config_progress_bar(content_length)

            self._view.set_main(self._model.bytes_to_human_readable(content_length))

            temp_file = None

            temp_dir = gettempdir()
            for filename in os.listdir(temp_dir):
                if re.match(rf'{self.software_name}_new_', filename):
                    temp_file = Path(temp_dir).resolve() / filename
                    if self._model.check_integrity(temp_file):
                        break
                    else:
                        temp_file = None

            if temp_file is None:
                temp_file = self._model.tmp_new_version_file_path(self.software_name)

                self._view.set_title('Downloading...')
                self._view.set_footer(f'Salvando em:/n{temp_file.name}')

                kwargs = {
                    'connection': connection,
                    'content_length': content_length,
                    'destination': temp_file,
                    'update_progress_bar_cmd': self._view.update_progress_bar,
                    'set_main_cmd': self._view.set_main,
                }
                self._model.download(**kwargs)

            self._view.set_main('Verificando integridade')

            if not self._model.check_integrity(temp_file):
                raise DownloadError('Arquivo baixado com problemas')

            self._view.set_title('Extraindo...')
            self._view.config_progress_bar(1)
            self._view.update_progress_bar(0)
            self._view.set_main('')
            self._view.set_footer('')

            self._model.extract_data(temp_file)

            self._view.set_title('Atualizando...')
            self._view.update_progress_bar(1)

            self._view.set_title('Inicializando...')

            subprocess.Popen(
                self.local / self.software_name / f'{self.software_name}.exe',
                shell=True,
                stdout=False,
                stderr=False,
            )

            self.close_window_event()

        except ConnectionError as e:
            self._view.set_title('Não foi possível se conectar à internet')
            self._view.set_main(str(e))
            self._view.set_footer('--------')
        except DownloadError as e:
            self._view.set_title('Falha')
            self._view.set_main(str(e))
            self._view.set_footer('--------')
        except requests.exceptions.ChunkedEncodingError:
            self._view.set_title('Não foi possível se conectar à internet')
            self._view.set_main('Conexão com servidor foi interrompida')
            self._view.set_footer('--------')
            self._update_process()

    def close_window_event(self):
        try:
            if self._model.bak_path:
                os.remove(self._model.bak_path)

            if self._model.tmp_new_version_path:
                os.remove(self._model.tmp_new_version_path)
        except Exception:
            pass

        os.kill(self._pid, signal.SIGTERM)
