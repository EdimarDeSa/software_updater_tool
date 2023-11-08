from argparse import ArgumentParser
import os
import signal
import subprocess
import urllib.parse
import tempfile as temp
import zipfile
import time
import shutil
import tkinter as tk
from pathlib import Path
from threading import Thread

import requests


ZIP = '.zip'
URL_BASE = 'https://www.efscode.com.br/atualizacoes/'
DOWNLOAD = 'downloads/'


class Atualizacao:
    def __init__(self, nome: str):
        self.nome_do_software = nome
        self.url_encodada = self.gera_url_atualizacao()
        self.pasta_software = self.busca_arquivo_local()

        self.bak_path: str = ''
        self.tmp_new_version_path: str = ''
        self.__pid = os.getpid()

        self.inicia_widgets()
        self.after(1000, self.inicia_thread)

    def inicia_thread(self):
        t1 = Thread(target=self.inicia_atualizacao)
        t1.start()

    def inicia_atualizacao(self):
        self.verifica_conexao_com_internet()
        self.gera_bkp()

    def inicia_widgets(self):
        ctk.CTk.__init__(self)
        self.geometry('550x300')
        self.title('QuestGenUpdater')
        ctk.set_default_color_theme('green')
        self.protocol(self.protocol()[0], self.evento_de_fechamento_da_tela)

        self.var_info = tk.StringVar()

        self.informacao = ctk.CTkLabel(self, text='')
        self.informacao.pack(pady=(20, 30))

        self.barra_de_progresso = ctk.CTkProgressBar(
            self,
            # progress_color='green',
            mode='determinate',
            orientation='horizontal',
        )
        self.barra_de_progresso.pack(padx=2, ipadx=200)
        self.barra_de_progresso.set(0)

        self.andamento_de_progresso = ctk.CTkLabel(self, text='')
        self.andamento_de_progresso.pack(fill='x', pady=(10, 0))

        self.velocidade_de_download = ctk.CTkLabel(self, text='', anchor='e')
        self.velocidade_de_download.pack(padx=(0, 20), pady=(10, 0))

    def verifica_conexao_com_internet(self) -> bool:
        self.atualiza_informacao('Verificando conexão com servidor.')
        try:
            requests.get(URL_BASE, timeout=100)
            return True
        except requests.exceptions.ConnectTimeout or requests.exceptions.ConnectionError:
            self.atualiza_informacao('Não foi possível se conectar à internet.')
            self.after(2000, self.evento_de_fechamento_da_tela)

    def gera_url_atualizacao(self) -> str:
        url_versao = URL_BASE + DOWNLOAD + self.nome_do_software + '.zip'
        encoded_url_versao = urllib.parse.quote(url_versao, safe=':/')
        return encoded_url_versao

    def gera_bkp(self):
        self.bak_path = temp.mktemp(prefix=f'{self.nome_do_software}_bak_')
        self.atualiza_informacao('Criando backup.')
        try:
            shutil.make_archive(self.bak_path, 'zip', self.pasta_software)
        except Exception as e:
            self.atualiza_informacao(f'Falha\n{e}\nao criar backup.')
            # Lidar com o erro adequadamente
        self.bak_path += '.zip'
        self.atualiza_informacao('Backup criado com sucesso.')

        self.baixar_nova_versao()

    def atualiza_informacao(self, informacao: str):
        self.informacao.configure(text=informacao)
        self.update_idletasks()

    def baixar_nova_versao(self):
        self.atualiza_informacao('Baixando nova versão.')
        response = requests.get(self.url_encodada, stream=True, timeout=100, )
        tamanho_total = int(response.headers.get('content-length', 0))
        tamanho_atual = 0
        inicio = time.time()

        with temp.NamedTemporaryFile(
                prefix=f'{self.nome_do_software}_new_', suffix=ZIP, delete=False
        ) as tmp_new_version:
            self.andamento_de_progresso.configure(text=tmp_new_version.name)
            for dados in response.iter_content(chunk_size=10000):
                tmp_new_version.write(dados)

                tamanho_atual += len(dados)
                self.calcula_velocidade(tamanho_atual, inicio)

                percentual_concluido = self.calcula_progresso(tamanho_atual, tamanho_total) * 100
                self.andamento_de_progresso.configure(text=f'{tmp_new_version.name} - {percentual_concluido:.2f}%')
                self.atualiza_barra_de_progresso(tamanho_atual, tamanho_total)

            self.atualiza_informacao('Testando download.')
            self.tmp_new_version_path = Path(str(tmp_new_version.name)).resolve()
        if zipfile.is_zipfile(self.tmp_new_version_path):
            self.atualiza_informacao('Download OK...')
            self.after(1000, lambda: self.atualiza_informacao('Iniciando atualização'))
            self.after(2000, self.atualiza)
        else:
            self.after(1000, lambda: self.atualiza_informacao('Falha no download'))
            self.after(2000, self.evento_de_fechamento_da_tela)

    def atualiza(self):
        with zipfile.ZipFile(self.tmp_new_version_path, 'r') as zip_ref:
            total_arquivos = len(zip_ref.namelist())
            self.andamento_de_progresso.configure(text=f'Extraindo arquivos... 0/{total_arquivos}')

            for index, arquivo in enumerate(zip_ref.namelist(), start=1):
                self.andamento_de_progresso.configure(text=f'Extraindo arquivos... {index}/{total_arquivos}')
                zip_ref.extract(arquivo, self.pasta_software)
                self.atualiza_barra_de_progresso(index, total_arquivos)
        self.andamento_de_progresso.configure(text='')
        self.atualiza_informacao(f'Iniciano: {self.nome_do_software}.exe')
        self.after(500, self.inicia_programa)

    def busca_arquivo_local(self):
        local = Path(__file__).resolve().parent
        if str(local) == r'C:\Users\Edimar\Documents\GitHub\gerador_de_questoes_didaxis':
            return local / r'compilado\dist'
        return local.parent / self.nome_do_software

    def atualiza_barra_de_progresso(self, valor_atual, valor_total):
        self.barra_de_progresso.set(self.calcula_progresso(valor_atual, valor_total))
        self.update_idletasks()

    @staticmethod
    def calcula_progresso(valor_atual, valor_total) -> float:
        try:
            progresso = valor_atual / valor_total
            return progresso
        except ZeroDivisionError:
            return 0

    def inicia_programa(self):
        comando = ['start', self.pasta_software / self.nome_do_software / f'{self.nome_do_software}.exe']
        try:
            subprocess.Popen(comando, shell=True)
        except Exception as e:
            print(e)

        self.andamento_de_progresso.configure(text='Tudo certo')
        self.after(1000, self.evento_de_fechamento_da_tela)

    def evento_de_fechamento_da_tela(self):
        try:
            if self.bak_path:
                os.remove(self.bak_path)

            if self.tmp_new_version_path:
                os.remove(self.tmp_new_version_path)
        except FileNotFoundError:
            pass

        os.kill(self.__pid, signal.SIGTERM)

    def calcula_velocidade(self, tamanho_atual, inicio):
        tempo_decorrido = time.time() - inicio
        velocidade = tamanho_atual / tempo_decorrido
        if velocidade < 1024:
            self.velocidade_de_download.configure(text=f"Velocidade: {velocidade:.2f} bytes/s")
        elif velocidade < 1024 * 1024:
            self.velocidade_de_download.configure(text=f"Velocidade: {velocidade / 1024:.2f} KB/s")
        else:
            self.velocidade_de_download.configure(text=f"Velocidade: {velocidade / (1024 * 1024):.2f} MB/s")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--name', '-n', type=str, required=True, help='Name of the software to update')

    app = Atualizacao(parser.parse_args.name)
    app.mainloop()
