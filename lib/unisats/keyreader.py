import os.path

DATAPATH_BASE = "./cache"


class NoteReader:
    def __init__(self):
        self.pairs = []

    def read(self, file: str):
        filep = os.path.join(DATAPATH_BASE, file)
        if os.path.exists(filep) is False:
            return

        with open(filep, "r") as t:
            y = t.readlines()
            full = [n.replace("\n", "") for n in y]
            t.close()
        self.pairs = full
