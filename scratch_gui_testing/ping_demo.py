#!/usr/bin/env python3
"""
Simple tkinter GUI demo showing verbose command execution with ping

This demonstrates how to:
1. Run a long-running command (ping) in a separate thread
2. Capture and display real-time output in a text widget
3. Show progress and status updates
4. Handle command completion
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import queue
import time
from pathlib import Path

class PingDemoApp:
    """Demo app showing verbose command execution with tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Ping Demo - Verbose Command Execution")
        self.root.geometry("600x500")
        
        # Communication between threads
        self.output_queue = queue.Queue()
        self.is_running = False
        
        self.setup_ui()
        self.start_output_monitoring()
    
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Ping Command Demo", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Host input
        ttk.Label(input_frame, text="Host to ping:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_entry = ttk.Entry(input_frame, width=30)
        self.host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.host_entry.insert(0, "google.com")  # Default value
        
        # Start/Stop buttons
        self.start_button = ttk.Button(input_frame, text="Start Ping", 
                                     command=self.start_ping)
        self.start_button.grid(row=0, column=2, padx=5)
        
        self.stop_button = ttk.Button(input_frame, text="Stop", 
                                    command=self.stop_ping, state="disabled")
        self.stop_button.grid(row=0, column=3, padx=5)
        
        # Output area with scrolling
        output_frame = ttk.LabelFrame(main_frame, text="Command Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        # Scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(output_frame, 
                                                   wrap=tk.WORD, 
                                                   height=20,
                                                   font=("Consolas", 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.grid_columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
    
    def start_ping(self):
        """Start ping command in background thread"""
        if self.is_running:
            return
            
        host = self.host_entry.get().strip()
        if not host:
            self.append_output("ERROR: Please enter a host to ping\n", "error")
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start(10)
        self.status_label.config(text=f"Pinging {host}...")
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        
        # Start ping in background thread
        self.ping_thread = threading.Thread(target=self._run_ping, args=(host,))
        self.ping_thread.daemon = True
        self.ping_thread.start()
    
    def stop_ping(self):
        """Stop the running ping command"""
        if hasattr(self, 'ping_process') and self.ping_process:
            try:
                self.ping_process.terminate()
                self.append_output("\n--- PING STOPPED BY USER ---\n", "warning")
            except:
                pass
        
        self._finish_ping()
    
    def _run_ping(self, host):
        """Run ping command and capture output"""
        try:
            # Windows ping command (5 pings)
            cmd = ["ping", "-n", "5", host]
            
            self.output_queue.put(("info", f"Running command: {' '.join(cmd)}\n"))
            self.output_queue.put(("info", "=" * 50 + "\n"))
            
            # Start the process
            self.ping_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Read output line by line
            while True:
                output = self.ping_process.stdout.readline()
                if output == '' and self.ping_process.poll() is not None:
                    break
                if output:
                    self.output_queue.put(("output", output))
            
            # Get any remaining output
            stdout, stderr = self.ping_process.communicate()
            if stdout:
                self.output_queue.put(("output", stdout))
            if stderr:
                self.output_queue.put(("error", f"ERROR: {stderr}"))
            
            # Check return code
            if self.ping_process.returncode == 0:
                self.output_queue.put(("success", "\n--- PING COMPLETED SUCCESSFULLY ---\n"))
            else:
                self.output_queue.put(("error", f"\n--- PING FAILED (exit code {self.ping_process.returncode}) ---\n"))
                
        except Exception as e:
            self.output_queue.put(("error", f"\nERROR: Failed to run ping: {e}\n"))
        finally:
            # Signal that we're done
            self.output_queue.put(("done", None))
    
    def start_output_monitoring(self):
        """Start monitoring the output queue"""
        self.process_output_queue()
    
    def process_output_queue(self):
        """Process messages from the output queue"""
        try:
            while True:
                try:
                    msg_type, content = self.output_queue.get_nowait()
                    
                    if msg_type == "done":
                        self._finish_ping()
                        break
                    elif content:
                        self.append_output(content, msg_type)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error processing output queue: {e}")
        
        # Schedule next check
        self.root.after(100, self.process_output_queue)
    
    def append_output(self, text, msg_type="output"):
        """Append text to output widget with appropriate styling"""
        # Configure text colors based on message type
        if msg_type == "error":
            self.output_text.insert(tk.END, text, "error")
        elif msg_type == "success":
            self.output_text.insert(tk.END, text, "success")
        elif msg_type == "warning":
            self.output_text.insert(tk.END, text, "warning")
        elif msg_type == "info":
            self.output_text.insert(tk.END, text, "info")
        else:
            self.output_text.insert(tk.END, text)
        
        # Auto-scroll to bottom
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def _finish_ping(self):
        """Clean up after ping completes or is stopped"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()
        self.status_label.config(text="Ready")
        
        if hasattr(self, 'ping_process'):
            self.ping_process = None
    
    def setup_text_tags(self):
        """Configure text widget styling"""
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("success", foreground="green")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("info", foreground="blue")

def main():
    """Run the ping demo application"""
    root = tk.Tk()
    app = PingDemoApp(root)
    app.setup_text_tags()
    
    print("🔧 Starting Ping Demo Application")
    print("This demonstrates verbose command execution with tkinter")
    print("Similar patterns can be used for pip install in venv_step")
    
    root.mainloop()

if __name__ == "__main__":
    main()