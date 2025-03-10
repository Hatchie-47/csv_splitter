import csv, os
import tkinter as tk
from tkinter import StringVar, IntVar
from pathlib import Path

class CSVProcessor:

    def __init__(self) -> None:
        self.path: Path = None
        self.header: list = None
        self.row_count: int = 0
        self.preview: dict[str: int] = None

    def change_file(self, path: StringVar, row_count: IntVar) -> None:
        self.path = Path(path.get())

        with open(self.path) as f:
            reader = csv.reader(f)
            for row in reader:
                self.header = row
                break

            self.row_count = sum(1 for _ in reader)
            row_count.set(self.row_count)


    def preview_files(self, n_files: int | None, n_rows: int | None) -> dict[str: int]:
        result = {}

        workable_path = os.path.join(self.path.parent, self.path.stem + '_{n}' + ''.join(self.path.suffixes))

        if n_files:
            base_rows: int = self.row_count // n_files
            remaining_rows: int = self.row_count % n_files

            for n in range(n_files):
                result[workable_path.format(n=n+1)] = base_rows if n >= remaining_rows else base_rows + 1
        else:
            remaining_rows:int = self.row_count
            n:int = 1
            while remaining_rows > 0:
                result[workable_path.format(n=n)] = min(remaining_rows, n_rows)
                remaining_rows -= n_rows
                n += 1

        self.preview = result
        return result


    def split_file(self, progress: tk.IntVar, label: tk.StringVar, root: tk.Tk) -> None:
        with open(self.path) as f:
            reader = csv.reader(f)
            header: list = next(reader)

            if ';'.join(header) != ';'.join(self.header):
                raise ValueError(f'File {self.path} changed!')

            step: int = 100 // len(self.preview)
            done: int = 0

            for k, v in self.preview.items():
                label.set(f'Creating {k} ...')
                done += step
                progress.set(done)
                root.update_idletasks()
                with open(k, 'w') as fn:
                    fn.write(';'.join(header))
                    for n in range(v):
                        fn.write('\n' + ';'.join(next(reader)))

            progress.set(100)
            label.set('Done!')
