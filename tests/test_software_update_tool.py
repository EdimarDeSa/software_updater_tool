from os.path import getsize
from urllib.parse import quote
from zipfile import ZipFile

import requests

import software_updater_tool as sut

SOFTWARENAME = 'gerador_de_questoes_didaxis'
URL = 'https://efscode.com.br/atualizacoes/downloads/gerador_de_questoes_didaxis.zip'


class TestDownload:
    entrada = requests.get(URL, stream=True, timeout=100)

    def test_status_code(self):
        # Verifique se o código de resposta HTTP é 200 (OK)
        assert (
            self.entrada.status_code == 200
        ), f'O download falhou com código de resposta {self.entrada.status_code}'

        # def test_tamanho_do_arquivo(self):
        #     # Verifique o tamanho do arquivo baixado (você pode ajustar o tamanho esperado)
        #     tamanho_esperado = 40628579  # Tamanho em bytes
        #     tamanho_baixado = len(self.entrada.content)
        #     assert tamanho_baixado == tamanho_esperado, f"O tamanho do arquivo baixado ({tamanho_baixado} bytes) não é o esperado"

        # def test_download(self):
        #     with open(f'{SOFTWARENAME}.zip', 'wb') as file:
        #         for chunk in self.entrada.iter_content(chunk_size=1024000):
        #             file.write(chunk)

        # Limpeza: feche a conexão
        self.entrada.close()

    def test_download_integritie(self):
        with ZipFile(file=f'{SOFTWARENAME}.zip') as zip_file:
            zip_file.extractall(f'{SOFTWARENAME}')
