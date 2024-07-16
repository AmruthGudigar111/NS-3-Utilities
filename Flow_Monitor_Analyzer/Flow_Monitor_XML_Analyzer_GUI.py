import tkinter as tk
from tkinter import ttk, filedialog
import xml.etree.ElementTree as ET

# Function to load and parse XML data
def load_xml(filename, progress_var):
    tree = ET.parse(filename)
    root = tree.getroot()
    progress_var.set(100)  # Update progress bar to indicate completion
    return root

# Function to extract all flow statistics
def extract_all_flow_stats(xml_root):
    flow_stats = []
    flow_stats_elem = xml_root.find("./FlowStats")
    if flow_stats_elem is not None:
        for flow_elem in flow_stats_elem.findall("./Flow"):
            flow_id = flow_elem.attrib.get("flowId", "")
            time_first_tx_packet = flow_elem.attrib.get("timeFirstTxPacket", "")
            time_first_rx_packet = flow_elem.attrib.get("timeFirstRxPacket", "")
            time_last_tx_packet = flow_elem.attrib.get("timeLastTxPacket", "")
            time_last_rx_packet = flow_elem.attrib.get("timeLastRxPacket", "")
            delay_sum = flow_elem.attrib.get("delaySum", "")
            jitter_sum = flow_elem.attrib.get("jitterSum", "")
            last_delay = flow_elem.attrib.get("lastDelay", "")
            tx_bytes = int(flow_elem.attrib.get("txBytes", 0))
            rx_bytes = int(flow_elem.attrib.get("rxBytes", 0))
            tx_packets = int(flow_elem.attrib.get("txPackets", 0))
            rx_packets = int(flow_elem.attrib.get("rxPackets", 0))
            lost_packets = int(flow_elem.attrib.get("lostPackets", 0))
            times_forwarded = int(flow_elem.attrib.get("timesForwarded", 0))
            
            # Calculate throughput in Mbps
            current_time = 30  # Example: replace with actual current time
            throughput_mbps = (rx_bytes * 8) / (1000000 * current_time)
            
            flow_stats.append((flow_id, time_first_tx_packet, time_first_rx_packet, 
                               time_last_tx_packet, time_last_rx_packet, delay_sum, 
                               jitter_sum, last_delay, tx_bytes, rx_bytes, tx_packets, 
                               rx_packets, lost_packets, times_forwarded, throughput_mbps))
    return flow_stats

# Function to handle file selection
def browse_file():
    filename = filedialog.askopenfilename(initialdir="/home/amruth/ns-allinone-3.41/ns-3.41/scratch",filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
    if filename:
        progress_var.set(0)  # Reset progress bar
        xml_root = load_xml(filename, progress_var)
        display_flow_stats(xml_root)

# Function to display flow statistics in table format
def display_flow_stats(xml_root):
    flow_stats = extract_all_flow_stats(xml_root)
    
    # Clear existing table
    for row in flow_stats_tree.get_children():
        flow_stats_tree.delete(row)
    
    # Insert new data into table
    for flow_stat in flow_stats:
        flow_stats_tree.insert("", tk.END, values=flow_stat)

# GUI setup
root = tk.Tk()
root.title("NS-3 Flow Monitor XML Analyzer by Amruth")

# Set Arial font with font size 10 for all widgets
style = ttk.Style()
style.configure('Arial.TButton', font=('Arial', 10))
style.configure('Arial.TLabel', font=('Arial', 10))
style.configure('Arial.TEntry', font=('Arial', 10))
style.configure('Arial.Treeview', font=('Arial', 10))

# Progress bar to indicate file reading progress
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, mode="determinate", variable=progress_var)
progress_bar.pack(fill="x", padx=10, pady=10)

# Label to browse for XML file
browse_label = ttk.Label(root, text="Browse the NS-3 Flow Monitor XML file:", style='Arial.TLabel')
browse_label.pack(pady=5)

# Browse button to select XML file
browse_button = ttk.Button(root, text="Browse", command=browse_file, style='Arial.TButton')
browse_button.pack(pady=5)

# Frame to contain the Treeview and Scrollbars
frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Treeview (table) to display flow statistics
columns = ("Flow ID", "Time First Tx Packet", "Time First Rx Packet", 
           "Time Last Tx Packet", "Time Last Rx Packet", "Delay Sum", 
           "Jitter Sum", "Last Delay", "TX Bytes", "RX Bytes", 
           "TX Packets", "RX Packets", "Lost Packets", "Times Forwarded", "Throughput (Mbps)")
flow_stats_tree = ttk.Treeview(frame, columns=columns, show="headings", style='Arial.Treeview')

# Configure column headings
for col in columns:
    flow_stats_tree.heading(col, text=col)
    flow_stats_tree.column(col, anchor="center")

# Vertical Scrollbar
vsb = ttk.Scrollbar(frame, orient="vertical", command=flow_stats_tree.yview)
flow_stats_tree.configure(yscrollcommand=vsb.set)
vsb.pack(side='right', fill='y')

# Horizontal Scrollbar
hsb = ttk.Scrollbar(frame, orient="horizontal", command=flow_stats_tree.xview)
flow_stats_tree.configure(xscrollcommand=hsb.set)
hsb.pack(side='bottom', fill='x')

# Pack the Treeview widget
flow_stats_tree.pack(fill="both", expand=True)

root.mainloop()
