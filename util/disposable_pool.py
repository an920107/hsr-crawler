from interface.disposable import Disposable

from threading import Timer
from uuid import UUID


class DisposablePool:

    def __init__(self) -> None:
        self.__pool = {}

    def __dispose(self, disposable_object: Disposable):
        disposable_object.dispose()
        self.__pool.pop(disposable_object.uuid)

    def add(self, disposable_object: Disposable) -> None:
        self.__pool[disposable_object.uuid] = disposable_object
        Timer(disposable_object.dispose_sec,
              lambda: self.__dispose(disposable_object)).start()

    def get(self, uuid: UUID) -> Disposable | None:
        return self.__pool.get(uuid)
