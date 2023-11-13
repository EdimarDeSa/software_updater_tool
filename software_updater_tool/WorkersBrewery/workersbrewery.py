from collections import deque
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from threading import Event, Thread
from time import sleep
from typing import Callable, Deque, Dict


@dataclass
class Quest:
    job: Callable
    job_kwargs: Dict = field(default_factory=dict)

    def execute(self):
        self.job(**self.job_kwargs)


class Worker(Thread):
    def __init__(
        self,
        name: str = '',
        interval: float = 0.0,
        daemon: bool = False,
        quest_board=None,
    ):
        super().__init__(daemon=daemon)

        self.name = f'worker_{name}' if name is not None else ''
        self.quest_board = quest_board
        self._quest = None
        self._interval = interval

        self._start_event = Event()
        self._stop_event = Event()
        self._reset_event = Event()

        self._running = False

        self._count_context = getcontext()
        self._count_context.prec = 2
        self._countdown_counter = Decimal('0', self._count_context)

        self.start()

    def run(self):
        while True:
            self._start_event.wait()

            self._reset_event.clear()
            self._running = True
            self._countdown_counter = Decimal('0', self._count_context)

            while self._running:
                self._countdown_counter += Decimal('0.1', self._count_context)

                if self._reset_event.is_set():
                    self._running = False

                if (
                    self._stop_event.is_set()
                    or self._countdown_counter >= self._wait_interval
                ):
                    self._running = False
                    self._job.execute()

                    self._stop_event.clear()
                    self._start_event.clear()

                sleep(0.1)

    def _start_countdown(self) -> None:
        self._wait_interval = Decimal(str(self._interval), self._count_context)
        self._reset_event.set()
        self._start_event.set()

    def stop_quests(self) -> None:
        self._stop_event.set()
        self._running = False
        self._quest = None

    def reset_countdown(self, new_interval=None) -> None:
        if new_interval is not None:
            self._wait_interval = Decimal(str(new_interval), self._count_context)
        self._reset_event.set()

    def set_job(self, quest: Quest) -> None:
        self._job = quest
        self._start_countdown()


@dataclass
class QuestContract:
    worker: Worker
    quest: Quest


class WorkersBrewery:
    def __init__(self, n_workers=2, wait_time=0.5, daemon_workers: bool = False):
        self.__stand_by_workers: Deque[Worker] = deque(maxlen=n_workers)
        self.__contracts: Dict[str, QuestContract] = dict()

        for id_ in range(n_workers):
            worker = Worker(str(id_), wait_time, daemon_workers)
            self.__stand_by_workers.append(worker)

    def hire_a_worker(
        self, contract_name: str, job: Callable, kwargs: Dict = None
    ) -> None:
        if kwargs is None:
            kwargs = dict()

        quest = Quest(job, kwargs)

        worker = self.__stand_by_workers.popleft()
        worker.set_job(quest)

        self.__contracts[contract_name] = QuestContract(worker, quest)

    def fire_a_worker(self, contract_name) -> None:
        contract = self._search_contract(contract_name)

        worker = contract.worker
        worker.stop_quests()
        self.__stand_by_workers.append(worker)

        del self.__contracts[contract_name]

    def update_a_contract(
        self, contract_name: str, quest_update: Callable, kwargs
    ) -> None:
        contract = self._search_contract(contract_name)

        contract.worker.reset_countdown()

        contract.quest = Quest(quest_update, kwargs)

    def _search_contract(self, contract_name: str) -> QuestContract:
        contract = self.__contracts.get(contract_name, None)

        if contract is None:
            raise KeyError('No such contract')

        return contract

    def exists_contract(self, contract_name: str) -> bool:
        return bool(self.__contracts.get(contract_name))
