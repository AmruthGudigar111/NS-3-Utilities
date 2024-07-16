import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import time
import threading

class FilterableTreeview(ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.filters = {}
        self.original_data = []

        self.heading("#0", text="")

        for col in self['columns']:
            self.heading(col, text=col, command=lambda _col=col: self.show_filter_menu(_col))

    def set_data(self, data):
        self.original_data = data
        self.update_displayed_data()

    def show_filter_menu(self, col):
        values = self.get_unique_values(col)
        menu = Menu(self, tearoff=0)
        menu.add_command(label="All", command=lambda: self.apply_filter(col, None))

        for value in values:
            menu.add_command(label=value, command=lambda _value=value: self.apply_filter(col, _value))

        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def get_unique_values(self, col):
        col_index = self['columns'].index(col)
        filtered_data = self.filter_data()
        values = list(set(item[col_index] for item in filtered_data))
        values.sort()
        return values

    def apply_filter(self, col, value):
        if value is None:
            self.filters.pop(col, None)
        else:
            self.filters[col] = value
        self.update_displayed_data()

    def filter_data(self):
        filtered_data = self.original_data
        for col, value in self.filters.items():
            col_index = self['columns'].index(col)
            filtered_data = [item for item in filtered_data if item[col_index] == value]
        return filtered_data

    def update_displayed_data(self):
        for item in self.get_children():
            self.delete(item)

        filtered_data = self.filter_data()

        for row in filtered_data:
            self.insert('', 'end', values=row)


def parse_data_chunk(data_chunk):
    parsed_chunk = []
    try:
        for line in data_chunk:
            parts = line.strip().split(", ")
            app = parts[0].split(": ")[1]
            context = parts[1].split(": ")[1]
            packet_id = int(parts[2].split(": ")[1])
            src_ip = parts[3].split(": ")[1]
            dst_ip = parts[4].split(": ")[1]
            parsed_chunk.append((packet_id, app, context, src_ip, dst_ip))
    except Exception as e:
        print(f"Error parsing data: {e}")
    return parsed_chunk

def load_data_from_file():
    file_path = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch", filetypes=[("Text files", "*.txt")])
    if file_path:
        read_file_with_progress(file_path)

def read_file_with_progress(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.readlines()
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file: {e}")
        return
    
    total_lines = len(data)
    progress_var.set(0)
    progress_label.config(text="Reading file...")

    chunk_size = 1000
    chunks = [data[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
    parsed_data = []
    threads = []
    
    start_time = time.time()

    def update_progress():
        while any(t.is_alive() for t in threads):
            completed_chunks = total_chunks - len([t for t in threads if t.is_alive()])
            progress = (completed_chunks / total_chunks) * 100
            progress_var.set(progress)
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / (completed_chunks + 1)) * total_chunks
            remaining_time = estimated_total_time - elapsed_time
            time_info.set(f"Elapsed: {elapsed_time:.2f}s, Remaining: {remaining_time:.2f}s")
            progress_label.config(text=f"Progress: {progress:.2f}%")
            time.sleep(0.1)

    total_chunks = len(chunks)
    
    for chunk in chunks:
        thread = threading.Thread(target=lambda c=chunk: parsed_data.extend(parse_data_chunk(c)))
        threads.append(thread)
        thread.start()
    
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.start()
    
    for thread in threads:
        thread.join()
    
    display_data(parsed_data)
    progress_label.config(text="File read successfully")

def display_data(parsed_data):
    tree.set_data(parsed_data)

# Main program entry point
if __name__ == "__main__":
    root = tk.Tk()
    root.title("NS-3 Packet Flow Data txt Analyzer by Amruth")

    # Browse button and label
    browse_frame = ttk.Frame(root)
    browse_frame.pack(padx=10, pady=10, fill=tk.X)
    
    browse_label = ttk.Label(browse_frame, text="Browse the packet_flow_log.txt file")
    browse_label.grid(row=0, column=0, padx=5, pady=5)
    
    browse_button = ttk.Button(browse_frame, text="Browse File", command=load_data_from_file)
    browse_button.grid(row=0, column=1, padx=5, pady=5)
    
    # Progress bar and label
    progress_frame = ttk.Frame(root)
    progress_frame.pack(padx=10, pady=10, fill=tk.X)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=5, pady=5)
    
    progress_label = ttk.Label(progress_frame, text="Progress: 0%")
    progress_label.pack(fill=tk.X, padx=5, pady=5)
    
    time_info = tk.StringVar()
    time_label = ttk.Label(progress_frame, textvariable=time_info)
    time_label.pack(fill=tk.X, padx=5, pady=5)
    
    # Treeview to display data
    columns = ('Packet ID', 'Application', 'Context', 'Source IP', 'Destination IP')
    tree = FilterableTreeview(root, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
    
    tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    root.mainloop()