import tkinter as tk
from tkinter import ttk, filedialog
import time
import threading

def parse_routing_data(data):
    nodes = {}
    lines = data.split('\n')
    current_node = None
    current_time = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("Node "):
            parts = line.split()
            current_node = int(parts[1])
            current_time = None
            if current_node not in nodes:
                nodes[current_node] = {
                    'ip_address': parts[-1],
                    'routing_tables': []
                }
        elif line.startswith("Node: "):
            parts = line.split(',')
            current_node = int(parts[0].split()[1])
            current_time = int(parts[1].split()[1][1:-1])
            nodes[current_node]['routing_tables'].append({
                'time': current_time,
                'routes': []
            })
        elif "Routing table" in line:
            continue
        elif "Destination" in line:
            continue
        elif "HNA" in line or "Priority" in line:
            continue
        elif line and current_node is not None:
            cols = line.split()
            if len(cols) == 4:
                route = {
                    'time': current_time,
                    'destination': cols[0],
                    'nexthop': cols[1],
                    'interface': cols[2],
                    'distance': cols[3]
                }
                nodes[current_node]['routing_tables'][-1]['routes'].append(route)
    
    return nodes

class RoutingTableAnalyzerApp(tk.Tk):
    def __init__(self, nodes=None):
        super().__init__()
        self.title("Routing Table Analyzer")
        self.geometry("800x600")
        
        self.nodes = nodes if nodes else {}
        
        self.create_widgets()

    def create_widgets(self):
        # Browse button and file label
        self.browse_button = tk.Button(self, text="Browse File", command=self.browse_file)
        self.browse_button.pack(side=tk.TOP, pady=5)
        
        self.file_label = tk.Label(self, text="Browse the RouteTable.txt file: No file selected")
        self.file_label.pack(side=tk.TOP, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side=tk.TOP, pady=5)
        
        self.progress_label = tk.Label(self, text="")
        self.progress_label.pack(side=tk.TOP, pady=5)
        
        # Notebook for multiple tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch",filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_label.config(text=f"Browse the RouteTable.txt file: {file_path}")
            self.load_file(file_path)

    def load_file(self, file_path):
        def read_file():
            with open(file_path, 'r') as f:
                lines = f.readlines()

            total_lines = len(lines)
            chunk_size = max(1, total_lines // 100)

            data = ""
            start_time = time.time()
            for i, line in enumerate(lines):
                data += line
                if i % chunk_size == 0:
                    self.update_progress(i / total_lines, start_time, i, total_lines)

            self.nodes = parse_routing_data(data)
            self.create_tabs()
            self.update_progress(1, start_time, total_lines, total_lines)

        threading.Thread(target=read_file).start()

    def update_progress(self, progress, start_time, current_line, total_lines):
        elapsed_time = time.time() - start_time
        if progress > 0:
            estimated_total_time = elapsed_time / progress
            remaining_time = estimated_total_time - elapsed_time
        else:
            estimated_total_time = 0
            remaining_time = 0

        self.progress_bar['value'] = progress * 100
        self.progress_label.config(
            text=f"{progress * 100:.2f}% completed. Time elapsed: {elapsed_time:.2f}s. "
                 f"Estimated remaining time: {remaining_time:.2f}s."
        )
        self.update_idletasks()

    def create_tabs(self):
        for node_id, node_data in self.nodes.items():
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Node {node_id+1}")
            
            tree = ttk.Treeview(tab, columns=("Time", "Destination", "NextHop", "Interface", "Distance"), show="headings")
            tree.heading("Time", text="Time", command=lambda: self.sort_treeview(tree, "Time", False))
            tree.heading("Destination", text="Destination", command=lambda: self.sort_treeview(tree, "Destination", False))
            tree.heading("NextHop", text="NextHop", command=lambda: self.sort_treeview(tree, "NextHop", False))
            tree.heading("Interface", text="Interface", command=lambda: self.sort_treeview(tree, "Interface", False))
            tree.heading("Distance", text="Distance", command=lambda: self.sort_treeview(tree, "Distance", False))
            tree.pack(fill=tk.BOTH, expand=True)

            # Populate treeview with routing table data
            for table in node_data['routing_tables']:
                for route in table['routes']:
                    if route['destination'] == 'HNA' or route['destination'] == 'Priority':
                        continue
                    tree.insert("", "end", values=(route['time'], route['destination'], route['nexthop'], route['interface'], route['distance']))

    def sort_treeview(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))


# Example usage:
app = RoutingTableAnalyzerApp()
app.mainloop()
