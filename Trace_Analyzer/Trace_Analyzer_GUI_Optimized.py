import re
import time
import csv
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

class TraceEntry:
    def __init__(self, time, event_type, rate, node, device, mac_header, llc_header, ipv4_header, udp_header, olsr_packet_header, olsr_message_header, src_ip, dst_ip):
        self.time = time
        self.event_type = event_type
        self.rate = rate
        self.node = node
        self.device = device
        self.mac_header = mac_header
        self.llc_header = llc_header
        self.ipv4_header = ipv4_header
        self.udp_header = udp_header
        self.olsr_packet_header = olsr_packet_header
        self.olsr_message_header = olsr_message_header
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def __repr__(self):
        return f"TraceEntry(time={self.time}, event_type={self.event_type}, rate={self.rate}, node={self.node}, device={self.device})"

def parse_time_event_rate(line):
    time_pattern = r"t\s([\d.]+)"
    event_pattern = r"(\w)\s([\d.]+)"
    rate_pattern = r"(\w+Rate[\d\w]+)"
    
    time_match = re.search(time_pattern, line)
    event_match = re.search(event_pattern, line)
    rate_match = re.search(rate_pattern, line)
    
    time = float(time_match.group(1)) if time_match else None
    event_type = event_match.group(1) if event_match else None
    event_time = float(event_match.group(2)) if event_match else None
    rate = rate_match.group(1) if rate_match else None
    
    return time, event_type, event_time, rate

def parse_node_device(line):
    node_device_pattern = r"/NodeList/(\d+)/DeviceList/(\d+)"
    node_device_match = re.search(node_device_pattern, line)
    
    node = int(node_device_match.group(1)) if node_device_match else None
    device = int(node_device_match.group(2)) if node_device_match else None
    
    return node, device

def parse_mac_header(line):
    mac_header_pattern = re.compile(r"ns3::WifiMacHeader \([^\)]*\)")
    mac_header_match = mac_header_pattern.search(line)
    return mac_header_match.group(0) if mac_header_match else None

def parse_llc_header(line):
    llc_header_pattern = re.compile(r"ns3::LlcSnapHeader \([^\)]*\)")
    llc_header_match = llc_header_pattern.search(line)
    return llc_header_match.group(0) if llc_header_match else None

def parse_ipv4_header(line):
    ipv4_header_pattern = re.compile(r"ns3::Ipv4Header \((.*)\)")
    ipv4_header_match = ipv4_header_pattern.search(line)
    if ipv4_header_match:
        nested_level = 1
        start_pos = ipv4_header_match.start(1)
        for i in range(start_pos + 1, len(line)):
            if line[i] == '(':
                nested_level += 1
            elif line[i] == ')':
                nested_level -= 1
                if nested_level == 0:
                    return line[ipv4_header_match.start():i + 1]
    return None

def extract_ips_from_ipv4_header(ipv4_header):
    if ipv4_header:
        ip_pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
        ips = ip_pattern.findall(ipv4_header)
        if len(ips) == 2:
            return ips[0], ips[1]
    return None, None

def parse_udp_header(line):
    udp_header_pattern = re.compile(r"ns3::UdpHeader \([^\)]*\)")
    udp_header_match = udp_header_pattern.search(line)
    return udp_header_match.group(0) if udp_header_match else None

def parse_olsr_packet_header(line):
    olsr_packet_header_pattern = re.compile(r"ns3::olsr::PacketHeader \([^\)]*\)")
    olsr_packet_header_match = olsr_packet_header_pattern.search(line)
    return olsr_packet_header_match.group(0) if olsr_packet_header_match else None

def parse_olsr_message_header(line):
    olsr_message_header_pattern = re.compile(r"ns3::olsr::MessageHeader \([^\)]*\)")
    olsr_message_header_match = olsr_message_header_pattern.search(line)
    return olsr_message_header_match.group(0) if olsr_message_header_match else None

def parse_trace_line(line):
    time, event_type, event_time, rate = parse_time_event_rate(line)
    node, device = parse_node_device(line)
    mac_header = parse_mac_header(line)
    llc_header = parse_llc_header(line)
    ipv4_header = parse_ipv4_header(line)
    udp_header = parse_udp_header(line)
    olsr_packet_header = parse_olsr_packet_header(line)
    olsr_message_header = parse_olsr_message_header(line)
    
    src_ip, dst_ip = extract_ips_from_ipv4_header(ipv4_header)
    
    return TraceEntry(event_time, event_type, rate, node, device, mac_header, llc_header, ipv4_header, udp_header, olsr_packet_header, olsr_message_header, src_ip, dst_ip)

def process_chunk(chunk, start_line):
    entries = []
    for i, line in enumerate(chunk):
        try:
            trace_entry = parse_trace_line(line)
            entries.append(trace_entry)
        except Exception as e:
            print(f"Error parsing line {start_line + i}: {e}")
    return entries

def read_trace_file(file_path, progress_callback=None):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    total_lines = len(lines)
    chunk_size = 10000
    chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]

    trace_entries = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_chunk, chunk, i * chunk_size): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            chunk_index = futures[future]
            try:
                result = future.result()
                trace_entries.extend(result)
                if progress_callback:
                    progress_percent = (chunk_index * chunk_size + len(result)) / total_lines * 100
                    elapsed_time = time.time() - start_time
                    estimated_total_time = elapsed_time / ((chunk_index * chunk_size + len(result)) / total_lines)
                    time_remaining = estimated_total_time - elapsed_time
                    progress_callback(progress_percent, elapsed_time, time_remaining)
            except Exception as e:
                print(f"Error processing chunk {chunk_index}: {e}")
    
    return trace_entries

class TraceAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NS3 Trace Analyzer by Amruth")
        self.geometry("1200x600")
        self.trace_entries = []

        self.create_widgets()

    def create_widgets(self):
        instruction_label = tk.Label(self, text="Browse the NS3 Trace File in *.tr format", font=("Arial", 10))
        instruction_label.pack(pady=10)
        
        self.file_button = tk.Button(self, text="Browse File", command=self.browse_file, font=("Arial", 10))
        self.file_button.pack(pady=10)
        
        self.progress_label = tk.Label(self, text="", font=("Arial", 10))
        self.progress_label.pack(pady=10)

        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        self.tree = ttk.Treeview(frame, columns=("Time", "Event Type", "Rate", "Node", "Source IP", "Destination IP", "Device", "Mac Header", "LLC Header", "IPv4 Header", "UDP Header", "OLSR Packet Header", "OLSR Message Header"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.filter_column(c))
            self.tree.column(col, width=200)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscroll=scrollbar_x.set)

        self.export_button = tk.Button(self, text="Export to CSV", command=self.export_to_csv, font=("Arial", 10))
        self.export_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch", filetypes=[("NS3 Trace Files", "*.tr")])
        if file_path:
            try:
                if file_path.endswith(".tr"):
                    self.trace_entries = read_trace_file(file_path, self.update_progress)
                    self.display_trace_entries(self.trace_entries)
                    self.progress_label.config(text="Reading file complete.")
                    self.progressbar.stop()
                else:
                    messagebox.showwarning("Invalid File", "Please select a valid NS3 trace file in *.tr format.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def display_trace_entries(self, trace_entries):
        for entry in self.tree.get_children():
            self.tree.delete(entry)
        
        for entry in trace_entries:
            display_event_type = "Transmit" if entry.event_type == 't' else "Receive" if entry.event_type == 'r' else entry.event_type
            display_node = f"N{entry.node + 1}" if entry.node is not None else ""
            self.tree.insert("", "end", values=(entry.time, display_event_type, entry.rate, display_node, entry.src_ip, entry.dst_ip, entry.device, entry.mac_header, entry.llc_header, entry.ipv4_header, entry.udp_header, entry.olsr_packet_header, entry.olsr_message_header))

    def update_progress(self, percent, elapsed_time, time_remaining):
        elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        time_remaining_str = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
        self.progress_label.config(text=f"Progress: {int(percent)}% | Elapsed Time: {elapsed_time_str} | Time Remaining: {time_remaining_str}")
        self.progressbar["value"] = percent
        self.update_idletasks()

    def filter_column(self, column):
        column_map = {
            "Time": "time",
            "Event Type": "event_type",
            "Rate": "rate",
            "Node": "node",
            "Source IP": "src_ip",
            "Destination IP": "dst_ip",
            "Device": "device",
            "Mac Header": "mac_header",
            "LLC Header": "llc_header",
            "IPv4 Header": "ipv4_header",
            "UDP Header": "udp_header",
            "OLSR Packet Header": "olsr_packet_header",
            "OLSR Message Header": "olsr_message_header",
        }
        
        attr = column_map[column]
        
        if attr == "node":
            unique_values = sorted(set(f"N{entry.node + 1}" for entry in self.trace_entries if entry.node is not None))
        else:
            unique_values = sorted(set(getattr(entry, attr) for entry in self.trace_entries if getattr(entry, attr) is not None))
        
        filter_window = tk.Toplevel(self)
        filter_window.title(f"Filter by {column}")
        filter_window.geometry("300x200")
        filter_window.transient(self)
        
        label = tk.Label(filter_window, text=f"Filter by {column}", font=("Arial", 10))
        label.pack(pady=10)

        filter_var = tk.StringVar(value="Select a value")

        filter_menu = ttk.Combobox(filter_window, textvariable=filter_var, values=unique_values, font=("Arial", 10))
        filter_menu.pack(pady=10)

        def apply_filter():
            selected_value = filter_var.get()
            if attr == "node":
                selected_value = selected_value[1:]  # Remove the "N" prefix to get the original node number
                filtered_entries = [entry for entry in self.trace_entries if entry.node is not None and f"N{entry.node + 1}" == selected_value]
            else:
                filtered_entries = [entry for entry in self.trace_entries if getattr(entry, attr) == selected_value]
            self.display_trace_entries(filtered_entries)
            filter_window.destroy()

        apply_button = tk.Button(filter_window, text="Apply Filter", command=apply_filter, font=("Arial", 10))
        apply_button.pack(pady=10)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(initialdir="/home/amruth/SERVER", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    headers = ["Time", "Event Type", "Rate", "Node", "Source IP", "Destination IP", "Device", "Mac Header", "LLC Header", "IPv4 Header", "UDP Header", "OLSR Packet Header", "OLSR Message Header"]
                    writer.writerow(headers)
                    for entry in self.trace_entries:
                        display_event_type = "Transmit" if entry.event_type == 't' else "Receive" if entry.event_type == 'r' else entry.event_type
                        display_node = f"N{entry.node + 1}" if entry.node is not None else ""
                        writer.writerow([entry.time, display_event_type, entry.rate, display_node, entry.src_ip, entry.dst_ip, entry.device, entry.mac_header, entry.llc_header, entry.ipv4_header, entry.udp_header, entry.olsr_packet_header, entry.olsr_message_header])
                messagebox.showinfo("Export Successful", "Data exported to CSV file successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = TraceAnalyzerApp()
    app.mainloop()
