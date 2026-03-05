import os
import re
import shutil
import io
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import subprocess
from pypdf import PdfReader
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

class NomencladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nomenclador Empresarial de Facturas")
        self.root.geometry("750x650")
        self.root.configure(bg="#F4F6F9")
        
        # Colores empresariales
        self.bg_color = "#F4F6F9"
        self.primary_blue = "#1A56DB"
        self.secondary_blue = "#3F83F8"
        self.dark_text = "#111827"
        self.light_text = "#6B7280"
        self.border_color = "#E5E7EB"
        self.success_color = "#059669"
        self.warning_color = "#D97706"

        self.source_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.aseguradora_sel = tk.StringVar(value="Rímac") # Default
        
        self.setup_styles()
        self.create_widgets()
        self.check_tesseract_status()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para Botón Principal
        style.configure("Primary.TButton", 
                        background=self.primary_blue, 
                        foreground="white", 
                        font=("Segoe UI", 11, "bold"),
                        padding=10,
                        borderwidth=0)
        style.map("Primary.TButton",
                  background=[('active', self.secondary_blue)])

        # Estilo para Botón Secundario
        style.configure("Secondary.TButton", 
                        background="white", 
                        foreground=self.dark_text, 
                        font=("Segoe UI", 10),
                        padding=5,
                        borderwidth=1,
                        bordercolor=self.border_color)
        style.map("Secondary.TButton",
                  background=[('active', '#F9FAFB')])
                  
        # Frame principal
        style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid", bordercolor=self.border_color)

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_blue, pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Nomenclador Universal de Facturas", font=("Segoe UI", 16, "bold"), bg=self.primary_blue, fg="white").pack()
        tk.Label(header_frame, text="Automatización de renombrado PDF mediante extracción de texto y OCR", font=("Segoe UI", 10), bg=self.primary_blue, fg="#D1D5DB").pack()

        # Contenedor Principal (Tarjeta)
        main_card = tk.Frame(self.root, bg="white", padx=25, pady=25, highlightbackground=self.border_color, highlightthickness=1)
        main_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Sección de Directorios
        paths_frame = tk.Frame(main_card, bg="white")
        paths_frame.pack(fill=tk.X, pady=(0, 20))

        # Origen
        tk.Label(paths_frame, text="Directorio de Origen", font=("Segoe UI", 10, "bold"), bg="white", fg=self.dark_text).pack(anchor="w")
        src_row = tk.Frame(paths_frame, bg="white")
        src_row.pack(fill=tk.X, pady=(5, 15))
        src_entry = tk.Entry(src_row, textvariable=self.source_dir, font=("Segoe UI", 10), bg="#F9FAFB", relief=tk.FLAT, highlightbackground=self.border_color, highlightthickness=1, highlightcolor=self.primary_blue)
        src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        ttk.Button(src_row, text="Examinar", style="Secondary.TButton", command=self.select_source, width=12).pack(side=tk.RIGHT)

        # Destino
        tk.Label(paths_frame, text="Directorio de Destino", font=("Segoe UI", 10, "bold"), bg="white", fg=self.dark_text).pack(anchor="w")
        out_row = tk.Frame(paths_frame, bg="white")
        out_row.pack(fill=tk.X, pady=(5, 15))
        out_entry = tk.Entry(out_row, textvariable=self.output_dir, font=("Segoe UI", 10), bg="#F9FAFB", relief=tk.FLAT, highlightbackground=self.border_color, highlightthickness=1, highlightcolor=self.primary_blue)
        out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        ttk.Button(out_row, text="Examinar", style="Secondary.TButton", command=self.select_output, width=12).pack(side=tk.RIGHT)

        # Selección de Aseguradora
        tk.Label(paths_frame, text="Seleccione la Aseguradora", font=("Segoe UI", 10, "bold"), bg="white", fg=self.dark_text).pack(anchor="w")
        aseg_row = tk.Frame(paths_frame, bg="white")
        aseg_row.pack(fill=tk.X, pady=(5, 10))
        aseguradoras = ["Rímac", "Pacífico"]
        aseg_combo = ttk.Combobox(aseg_row, textvariable=self.aseguradora_sel, values=aseguradoras, state="readonly", font=("Segoe UI", 10))
        aseg_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        aseg_combo.current(0)

        # Estado OCR y Controles
        control_frame = tk.Frame(main_card, bg="white")
        control_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_tess_status = tk.Label(control_frame, text="Estado motor OCR:", font=("Segoe UI", 9), bg="white", fg=self.light_text)
        self.lbl_tess_status.pack(side=tk.LEFT)
        
        self.lbl_tess_indicator = tk.Label(control_frame, text="Verificando...", font=("Segoe UI", 9, "bold"), bg="white")
        self.lbl_tess_indicator.pack(side=tk.LEFT, padx=5)
        
        self.btn_install_tess = tk.Button(control_frame, text="Instalar Tesseract", bg=self.warning_color, fg="white", font=("Segoe UI", 8, "bold"), relief=tk.FLAT, command=self.install_tesseract, padx=10, pady=2, cursor="hand2")

        self.start_btn = ttk.Button(control_frame, text="INICIAR PROCESAMIENTO", style="Primary.TButton", command=self.start_processing)
        self.start_btn.pack(side=tk.RIGHT)

        # Consola Log
        tk.Label(main_card, text="Registro del Sistema", font=("Segoe UI", 10, "bold"), bg="white", fg=self.dark_text).pack(anchor="w", pady=(15, 5))
        
        log_frame = tk.Frame(main_card, bg="#111827", padx=1, pady=1) # Borde oscuro faux
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, bg="#1E293B", fg="#A7F3D0", font=("Consolas", 9), relief=tk.FLAT, borderwidth=0)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log("Sistema inicializado. Esperando instrucciones...")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def select_source(self):
        folder = filedialog.askdirectory(title="Seleccionar Directorio de Origen")
        if folder:
            self.source_dir.set(folder)

    def select_output(self):
        folder = filedialog.askdirectory(title="Seleccionar Directorio de Destino")
        if folder:
            self.output_dir.set(folder)

    def check_tesseract_status(self):
        if not pytesseract:
            self.lbl_tess_indicator.config(text="Librería faltante", fg="#EF4444")
            self.btn_install_tess.pack(side=tk.LEFT, padx=10)
            return False

        tesseract_cmd = shutil.which("tesseract")
        found_path = None
        if tesseract_cmd:
            found_path = tesseract_cmd
        else:
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\siste\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            for p in common_paths:
                if os.path.exists(p):
                    found_path = p
                    break
                    
        if found_path:
            pytesseract.pytesseract.tesseract_cmd = found_path
            self.lbl_tess_indicator.config(text="Activo y Funcionando", fg=self.success_color)
            self.btn_install_tess.pack_forget()
            self.log("[SISTEMA] Motor OCR (Tesseract) verificado exitosamente.")
            return True
        else:
            self.lbl_tess_indicator.config(text="Motor no instalado", fg="#EF4444")
            self.btn_install_tess.pack(side=tk.LEFT, padx=10)
            self.log("[ADVERTENCIA] Motor OCR no detectado. Esencial para PDFs escaneados.")
            return False

    def install_tesseract(self):
        self.btn_install_tess.config(state=tk.DISABLED, text="Instalando...", bg="#9CA3AF")
        self.log("[SISTEMA] Iniciando descarga de Tesseract OCR...")
        
        def run_install():
            ps_script = """
            $url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
            $out = "$env:TEMP\\tesseract-setup.exe"
            Invoke-WebRequest -Uri $url -OutFile $out
            Start-Process -FilePath $out -ArgumentList "/SILENT" -Wait
            """
            try:
                subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
                self.log("[SISTEMA] Instalación de Tesseract finalizada con éxito.")
                self.root.after(1000, self.check_tesseract_status)
            except Exception as e:
                self.log(f"[ERROR] Fallo instalando Tesseract: {e}")
            finally:
                self.btn_install_tess.config(state=tk.NORMAL, text="Instalar Tesseract", bg=self.warning_color)

        threading.Thread(target=run_install, daemon=True).start()

    def extract_text_from_images(self, path):
        if not pytesseract or not self.check_tesseract_status():
            return ""
        
        try:
            reader = PdfReader(path)
            if len(reader.pages) == 0:
                return ""
            
            page = reader.pages[0]
            text_content = ""
            
            if page.images:
                for image_file_object in page.images:
                    try:
                        image_data = image_file_object.data
                        image = Image.open(io.BytesIO(image_data))
                        text = pytesseract.image_to_string(image)
                        text_content += text + "\n"
                    except Exception:
                        pass
        except Exception:
            return ""
        return text_content

    def find_invoice_data(self, text):
        match = re.search(r"\b([A-Za-z0-9]{4})[-\s]+(\d{8})\b", text)
        if match:
            return match.group(1).upper(), match.group(2)
        match = re.search(r"(?:Factura|Serie|Folio).*?([A-Za-z0-9]{4})[-\s]*(\d{8})", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).upper(), match.group(2)
        return None, None

    def process_file(self, file_path, output_dir, aseguradora):
        filename = os.path.basename(file_path)
        self.log(f" > Analizando: {filename}")
        
        try:
            reader = PdfReader(file_path)
            text = reader.pages[0].extract_text()
        except Exception as e:
            text = ""

        if not text or len(text.strip()) < 15:
            self.log("   Requiere OCR: Escaneando imagen...")
            ocr_text = self.extract_text_from_images(file_path)
            if ocr_text:
                text += "\n" + ocr_text

        series, number = self.find_invoice_data(text)

        if series and number:
            if aseguradora == "Rímac":
                new_name = f"20526109237_01_{series}_{number}.pdf"
            elif aseguradora == "Pacífico":
                new_name = f"FA-{series}-{number}.pdf"
            else:
                new_name = f"{series}_{number}.pdf" # Fallback

            new_path = os.path.join(output_dir, new_name)
            
            try:
                shutil.copy2(file_path, new_path)
                self.log(f"   [ÉXITO] Identificado: {series}-{number}")
                self.log(f"   [GUARDADO] {new_name}")
            except Exception as e:
                self.log(f"   [ERROR] Fallo de guardado: {e}")
        else:
            self.log("   [ERROR] Documento no reconocido/ilegible.")
            error_path = os.path.join(output_dir, f"ERROR_{filename}")
            try:
                shutil.copy2(file_path, error_path)
            except:
                pass

    def start_processing(self):
        source = self.source_dir.get()
        output = self.output_dir.get()
        aseguradora = self.aseguradora_sel.get()

        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "El directorio de origen no es válido.")
            return
        if not output or not os.path.exists(output):
            messagebox.showerror("Error", "El directorio de destino no es válido.")
            return

        self.start_btn.config(state=tk.DISABLED, text="PROCESANDO...")
        
        def run():
            files = [f for f in os.listdir(source) if f.lower().endswith('.pdf')]
            self.log(f"\n[INICIO] Aseguradora: {aseguradora}")
            self.log(f"Iniciando lote de {len(files)} archivos PDF.\n" + "-"*50)
            
            for f in files:
                file_path = os.path.join(source, f)
                self.process_file(file_path, output, aseguradora)
                
            self.log("-" * 50 + "\n[FINALIZADO] Proceso concluido satisfactoriamente.\n")
            self.start_btn.config(state=tk.NORMAL, text="INICIAR PROCESAMIENTO")

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NomencladorApp(root)
    root.mainloop()
