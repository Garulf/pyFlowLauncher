from ..base import Base
from ids import ID


class Server(Base):

    def __init__(self, id: ID):
        self.id = id