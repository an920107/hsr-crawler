from uuid import UUID, uuid4


class Disposable:

    def __init__(self, uuid: UUID = None, dispose_sec: float | None = None) -> None:
        self.uuid = uuid if uuid != None else uuid4()
        self.dispose_sec = dispose_sec

    def dispose(self) -> None:
        pass
