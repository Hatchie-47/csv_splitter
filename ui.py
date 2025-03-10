import tkinter as tk
from tkinter import filedialog, ttk
from csv_processor import CSVProcessor

class Root(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.title('CSV splitter')
        self.geometry('1000x500')
        self.minsize(1000, 500)

        self.processor: CSVProcessor = CSVProcessor()

        self.file_frame: tk.Frame = FileFrame(self)
        self.file_frame.pack(anchor='nw', padx=10, pady=10, fill='x')

        self.process_frame: tk.Frame = ProcessFrame(self)


    def open_file(self) -> None:
        self.file_frame.file_path_text.set(filedialog.askopenfilename(filetypes = [('csv', '*.csv')]))
        self.processor.change_file(self.file_frame.file_path_text, self.process_frame.row_count_text)
        self.process_frame.pack(anchor='nw', padx=10, expand=True, fill='both')
        self.check_state('path')


    def check_state(self, path, *args, **kwargs) -> None:
        enable: bool = False

        self.process_frame.treeview.delete(*self.process_frame.treeview.get_children())
        self.process_frame.progress_bar.grid_forget()
        self.process_frame.progress_label_var.set('')

        match path:
            case 'path':
                self.process_frame.split_mode_var.set('none')
                self.process_frame.n_var.set(0)
            case 'split_mode':
                self.process_frame.n_var.set(0)
            case 'n':
                try:
                    n:int = self.process_frame.n_var.get()
                except:
                    n = 0

                if n > 0:
                    enable = self.preview_split()
            case _:
                raise ValueError

        if enable:
            self.process_frame.run_button.config(state='active')
        else:
            self.process_frame.run_button.config(state='disabled')


    def preview_split(self) -> bool:
        preview: dict[str, int] = None

        n = self.process_frame.n_var.get()

        match self.process_frame.split_mode_var.get():
            case 'files':
                preview = self.processor.preview_files(n, None)
            case 'rows':
                preview = self.processor.preview_files(None, n)
            case _:
                pass

        for k, v in preview.items():
            self.process_frame.treeview.insert('', 'end', values=(k, v))

        return True if preview else False


    def split_file(self) -> None:
        self.process_frame.progress_bar.grid(column=0, row=3, columnspan=8, padx=10, pady=(2, 10), sticky='sew')
        self.processor.split_file(self.process_frame.progress_var, self.process_frame.progress_label_var, self)


    def display_column(self) -> None:
        raise NotImplementedError


class FileFrame(tk.Frame):

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.parent = parent

        self.columnconfigure(1, weight=1)

        self.file_label: tk.Label = tk.Label(self, text='File:')
        self.file_label.grid(column=0, row=0)

        self.file_path_text: tk.StringVar = tk.StringVar(name='file_path')
        self.file_path: tk.Entry = tk.Entry(self, state='readonly', textvariable=self.file_path_text)
        self.file_path.grid(column=1, row=0, padx=10, sticky='ew')

        self.file_button: tk.Button = tk.Button(self, text='Open file', command=self.parent.open_file)
        self.file_button.grid(column=2, row=0, padx=10)


class ProcessFrame(tk.Frame):

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.parent = parent

        self.pack(anchor='nw', padx=10, expand=True, fill='both')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.rowconfigure(1, weight=1)

        # Number of rows in file
        self.row_count_label: tk.Label = tk.Label(self, text='Number of data rows:')
        self.row_count_label.grid(column=0, row=0, padx=10, pady=10, sticky='e')

        self.row_count_text: tk.IntVar = tk.IntVar(name='row_count')
        self.row_count: tk.Entry = tk.Entry(self, state='readonly', textvariable=self.row_count_text)
        self.row_count.grid(column=1, row=0, padx=10, pady=10, sticky='ew')

        # Picking options
        self.split_mode_var: tk.StringVar = tk.StringVar(name='split_mode')
        self.split_mode_var.set('none')
        self.split_mode_var.trace_add('write', self.parent.check_state)

        self.by_number_button: tk.Radiobutton = tk.Radiobutton(self,
                                                               value = 'files',
                                                               variable=self.split_mode_var)
        self.by_number_button.grid(column=2, row=0, padx=0, pady=10, sticky='e')

        self.by_number_label: tk.Label = tk.Label(self, text='Split to N equal files')
        self.by_number_label.grid(column=3, row=0, padx=0, pady=10, sticky='w')

        self.by_rows_button: tk.Radiobutton = tk.Radiobutton(self,
                                                             value='rows',
                                                             variable=self.split_mode_var)
        self.by_rows_button.grid(column=4, row=0, padx=0, pady=10, sticky='e')

        self.by_rows_label: tk.Label = tk.Label(self, text='Split by N rows')
        self.by_rows_label.grid(column=5, row=0, padx=0, pady=10, sticky='w')

        self.n_label: tk.Label = tk.Label(self, text='The N:')
        self.n_label.grid(column=6, row=0, padx=10, pady=10, sticky='e')

        self.n_var: tk.IntVar = tk.IntVar(name='n')
        self.n_var.trace_add('write', self.parent.check_state)
        self.n_count: tk.Entry = tk.Entry(self, textvariable=self.n_var)
        self.n_count.grid(column=7, row=0, padx=10, pady=10, sticky='ew')

        self.header_button: tk.Button = tk.Button(self, text='Columns',
                                                  command=self.parent.display_column,
                                                  state='disabled')
        self.header_button.grid(column=8, row=0, padx=10, pady=10, sticky='e')

        # Treeview
        self.treeview: ttk.Treeview = ttk.Treeview(self, columns=('name', 'rows'), show='headings')
        self.treeview.heading('name', text='name')
        self.treeview.heading('rows', text='rows')
        self.treeview.grid(column=0, row=1, columnspan=9, padx=10, pady=(10, 2), sticky='nsew')

        # Progress and split button
        self.progress_label_var: tk.StringVar = tk.StringVar(name='progress_label')
        self.progress_label: tk.Label = tk.Label(self, textvariable=self.progress_label_var)
        self.progress_label.grid(column=0, row=2, padx=10, pady=2, sticky='sw')

        self.progress_var: tk.IntVar = tk.IntVar(name='progress')
        self.progress_bar: ttk.Progressbar = ttk.Progressbar(self,
                                                             orient='horizontal',
                                                             mode='determinate',
                                                             variable=self.progress_var,
                                                             style='Striped.Horizontal.TProgressbar')
        self.progress_bar.grid(column=0, row=3, columnspan=8, padx=10, pady=(2, 10), sticky='sew')

        self.run_button: tk.Button = tk.Button(self,
                                               text='Split file',
                                               command=self.parent.split_file,
                                               state='disabled')
        self.run_button.grid(column=8, row=3, padx=10, pady=(2, 10), sticky='se')

        self.progress_var.set(0)
        self.progress_label.config(text='')
        self.progress_bar.grid_forget()

        self.pack_forget()
