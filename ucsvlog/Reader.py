import codecs

READ_SIZE = 100000
NEW_LINE_MARK = '\n'
NEW_CELL = '"'
CELLS_DELIMITER = ','

NEW_LINE_SPLIT = NEW_LINE_MARK + NEW_CELL
NEW_CELL_SPLIT = CELLS_DELIMITER + NEW_CELL
ESCAPED_CELL = NEW_CELL + NEW_CELL


def count_first_quotes(data):
    q_len = 0
    for item in data:
        if item != NEW_CELL:
            break
        q_len += 1
    return q_len


class Reader(object):
    def __init__(self, filename, seek=0, close_row=None):
        self.filename = filename
        self.fh = codecs.open(filename, 'r', 'utf-8')
        self.close_row = close_row
        if seek:
            self.fh.seek(seek)
        self._last_record = ''

    def import_all(self):
        #will be removed in future
        list(self.all_records())

    def all_records(self):
        while True:
            records = self.read_records()
            if records is None:
                break

            for record in records:
                if self.close_row is None:
                    yield self.write_row(self.split_cells(record))
                else:
                    cells = self.split_cells(record)
                    if cells[-1] == self.close_row:
                        yield self.write_row(cells[:-1])

    def read_data(self):
        data = self.fh.read(READ_SIZE)
        if not data:
            return
        while data[-1]  in '"':
            next_read = self.fh.read(1)
            if not next_read:
                break
            data += next_read
        data = self._last_record + data
        self._last_record = ''
        return data

    def read_records(self):
        data = self.read_data()
        if data is None:
            if not self._last_record:
                return
            data = self._last_record
            self._last_record = None

        #note: first line is always fail
        records = []
        for record in data.split(NEW_LINE_SPLIT)[1:]:
            if record.startswith(NEW_CELL) and  count_first_quotes(record) % 2:
                if records:
                    records[-1] += NEW_LINE_SPLIT + record
                continue
            records.append(record)

        if self._last_record is None:
            return records

        if len(records) <= 1:
            self._last_record = data
            return self.read_records()

        self._last_record = NEW_LINE_SPLIT + records.pop()
        return records

    def split_cells(self, data):
        cells = []
        raw_cells = data.split(NEW_CELL_SPLIT)
        cells.append(raw_cells.pop(0).replace(ESCAPED_CELL, NEW_CELL))
        for cell in raw_cells:
            if cell.startswith(NEW_CELL) and  count_first_quotes(cell) % 2:
                cells[-1] += (NEW_CELL_SPLIT + cell).\
                                replace(ESCAPED_CELL, NEW_CELL)
            else:
                cells.append(cell.replace(ESCAPED_CELL, NEW_CELL))
        return cells

    def tell(self):
        return self.fh.tell()

    def write_row(self, row):
        return row
