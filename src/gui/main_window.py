import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess
import shutil
import threading
import json
from ..utils.lune_installer import LuneInstaller


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Rblx 2 Rojo Converter")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.selected_file = None
        self.output_dir = None
        
        install_dir = Path.home() / ".rblx2rojo" / "lune"
        self.lune_installer = LuneInstaller(install_dir)
        self.lune_path = None
        
        self.services = {
            "ServerScriptService": tk.BooleanVar(value=True),
            "ReplicatedStorage": tk.BooleanVar(value=True),
            "ServerStorage": tk.BooleanVar(value=True),
            "StarterPlayer": tk.BooleanVar(value=True),
            "StarterGui": tk.BooleanVar(value=True),
            "ReplicatedFirst": tk.BooleanVar(value=True),
        }
        
        self.panel_open = False
        self.side_panel = None
        
        self._setup_ui()
        
        self.root.after(100, self._check_lune)
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        self.menu_button = tk.Button(
            header_frame,
            text="☰",
            font=("Arial", 18),
            width=3,
            height=1,
            relief=tk.FLAT,
            command=self._toggle_panel,
            cursor="hand2"
        )
        self.menu_button.pack(side=tk.LEFT, padx=(0, 15))
        
        title = ttk.Label(header_frame, text="Roblox 2 Rojo Converter", font=("Arial", 16, "bold"))
        title.pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="RBXL/RBXM File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_entry = ttk.Entry(main_frame, width=40)
        self.file_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self._browse_file).grid(row=1, column=2, pady=5)
        
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(main_frame, width=40)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self._browse_output).grid(row=2, column=2, pady=5)
        
        self.convert_button = ttk.Button(
            main_frame, 
            text="Convert to Rojo Project",
            command=self._convert,
            state=tk.DISABLED
        )
        self.convert_button.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.progress = ttk.Progressbar(main_frame, length=400, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.status_text = tk.Text(main_frame, height=10, width=70, state=tk.DISABLED)
        self.status_text.grid(row=5, column=0, columnspan=3, pady=10)
        
        scrollbar = ttk.Scrollbar(main_frame, command=self.status_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.status_text.config(yscrollcommand=scrollbar.set)
    
    def _toggle_panel(self):
        if self.panel_open:
            self._close_panel()
        else:
            self._open_panel()
    
    def _open_panel(self):
        if self.side_panel:
            return
        
        self.panel_open = True
        self.side_panel = tk.Toplevel(self.root)
        self.side_panel.title("Service Filter")
        self.side_panel.geometry(f"250x300+{self.root.winfo_x()}+{self.root.winfo_y()}")
        self.side_panel.resizable(False, False)
        self.side_panel.protocol("WM_DELETE_WINDOW", self._close_panel)
        
        panel_frame = ttk.Frame(self.side_panel, padding="20")
        panel_frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(panel_frame, text="Services to Include", font=("Arial", 12, "bold"))
        title.pack(pady=(0, 15))
        
        for service_name, var in self.services.items():
            cb = ttk.Checkbutton(
                panel_frame,
                text=service_name,
                variable=var,
                onvalue=True,
                offvalue=False
            )
            cb.pack(anchor=tk.W, pady=5)
    
    def _close_panel(self):
        if self.side_panel:
            self.side_panel.destroy()
            self.side_panel = None
        self.panel_open = False
    
    def _browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select RBXL/RBXM File",
            filetypes=[
                ("Roblox Files", "*.rbxl *.rbxm"),
                ("Roblox Place Files", "*.rbxl"),
                ("Roblox Model Files", "*.rbxm"),
                ("Roblox XML Files", "*.rbxlx *.rbxmx"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.selected_file = Path(filename)
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, str(self.selected_file))
            
            if not self.output_dir:
                default_output = self.selected_file.parent / f"{self.selected_file.stem}_rojo"
                self.output_dir = default_output
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, str(self.output_dir))
            
            self._check_ready()
    
    def _browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        
        if directory:
            self.output_dir = Path(directory)
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, str(self.output_dir))
            self._check_ready()
    
    def _check_ready(self):
        if self.selected_file and self.output_dir:
            self.convert_button.config(state=tk.NORMAL)
    
    def _log(self, message: str):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def _check_lune(self):
        if self.lune_installer.is_installed():
            self.lune_path = str(self.lune_installer.lune_path)
            self._log(f"✓ Lune found at: {self.lune_path}")
            return
        
        if shutil.which("lune"):
            try:
                result = subprocess.run(
                    ["lune", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.lune_path = "lune"
                    self._log("✓ Lune found in PATH")
                    return
            except (subprocess.TimeoutExpired, Exception):
                pass
        
        result = messagebox.askyesno(
            "Lune Not Found",
            "Lune runtime is required for this tool.\n\n"
            "Would you like to download and install Lune automatically?\n\n"
            "(It will be installed locally in ~/.rblx2rojo/lune)",
            icon="question"
        )
        
        if not result:
            self._log("✗ Lune installation declined. Exiting...")
            messagebox.showinfo(
                "Installation Required",
                "Please install Lune manually from:\nhttps://lune-org.github.io/docs"
            )
            self.root.after(500, self.root.quit)
            return
        
        self._install_lune()
    
    def _install_lune(self):
        self.convert_button.config(state=tk.DISABLED)
        self.progress.start()
        
        def install_worker():
            try:
                def progress_callback(msg):
                    self.root.after(0, self._log, msg)
                
                path = self.lune_installer.download_and_install(progress_callback)
                self.lune_path = path
                self.root.after(0, self._on_install_success)
            except Exception as e:
                self.root.after(0, self._on_install_error, str(e))
        
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()
    
    def _on_install_success(self):
        self.progress.stop()
        self.convert_button.config(state=tk.NORMAL if (self.selected_file and self.output_dir) else tk.DISABLED)
    
    def _on_install_error(self, error_msg: str):
        self.progress.stop()
        self._log(f"✗ Installation failed: {error_msg}")
        messagebox.showerror(
            "Installation Failed",
            f"Failed to install Lune:\n{error_msg}\n\n"
            "Please install Lune manually from:\nhttps://lune-org.github.io/docs"
        )
        self.root.after(500, self.root.quit)
    
    def _convert(self):
        try:
            self.convert_button.config(state=tk.DISABLED)
            self.progress.start()
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state=tk.DISABLED)
            
            self._log(f"Starting conversion of {self.selected_file.name}...")
            
            if not self.lune_path:
                raise Exception("Lune is not available. Please restart the application.")
            
            script_path = Path(__file__).parent.parent / "converters" / "convert.luau"
            
            if not script_path.exists():
                raise Exception(f"Conversion script not found at: {script_path}")
            
            self._log("Running Lune conversion script...")
            
            input_file_str = str(self.selected_file.resolve())
            output_dir_str = str(self.output_dir.resolve())
            script_path_str = str(script_path.resolve())
            
            enabled_services = [name for name, var in self.services.items() if var.get()]
            services_json = json.dumps(enabled_services)
            
            result = subprocess.run(
                [self.lune_path, "run", script_path_str, input_file_str, output_dir_str, services_json],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Lune conversion failed: {result.stderr}")
            
            for line in result.stdout.strip().split("\n"):
                self._log(line)
            
            self.progress.stop()
            messagebox.showinfo("Success", "Conversion completed successfully!")
            
        except Exception as e:
            self.progress.stop()
            self._log(f"\n✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        
        finally:
            self.convert_button.config(state=tk.NORMAL)
