from uuid import UUID, uuid4


class Disposable:

    def __init__(self, uuid: UUID = uuid4(), dispose_sec: float | None = None) -> None:
        self.uuid = uuid
        self.dispose_sec = dispose_sec

    def dispose(self) -> None:
        pass
