import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from logic import ImageToPixelArtConverter

# Imposta il tema Dark moderno di default
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PixelArtApp(ctk.CTk):
    def __init__(self, converter):
        super().__init__()
        self.converter = converter

        # Configurazione Finestra Principale
        self.title("Pixel Art Studio")
        self.geometry("950x600")
        self.minsize(850, 550)

        # Variabili di stato
        self.input_path = None
        
        # Variabili per gestire i campi di testo
        self.str_dim_main = ctk.StringVar(value="64")
        self.str_dim_sec = ctk.StringVar(value="64")
        
        # Aggiorna automaticamente il lato minore mentre l'utente digita
        self.str_dim_main.trace_add("write", self._update_proportions)

        # Layout a 2 colonne
        self.grid_columnconfigure(0, weight=0) # Mantiene la sidebar fissa
        self.grid_columnconfigure(1, weight=1) # Fa espandere l'anteprima
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_preview_area()

    # ------------------------------------------------------------------
    # FUNZIONE HELPER: Scala l'immagine per la UI senza distorcerla e SENZA SFOCARLA
    # ------------------------------------------------------------------
    def _create_fitted_ctk_image(self, pil_img, max_size=280, is_pixel_art=False):
        """Crea una CTkImage ridimensionata mantenendo le proporzioni e la nitidezza dei pixel"""
        w, h = pil_img.size
        # Trova il rapporto di scala per rientrare nel riquadro max_size x max_size
        ratio = min(max_size / w, max_size / h)
        new_w = max(1, int(w * ratio))
        new_h = max(1, int(h * ratio))
        
        # Se stiamo gestendo la Pixel Art, usiamo Image.NEAREST per ingrandire
        # a blocchi netti ed evitare il filtro di sfocatura (antialias) di CustomTkinter
        if is_pixel_art:
            pil_img = pil_img.resize((new_w, new_h), Image.NEAREST)

        return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))

    # ------------------------------------------------------------------
    # 1. PANNELLO DI SINISTRA (CONTROLLI)
    # ------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Titolo App
        title = ctk.CTkLabel(sidebar, text="Pixel Art Studio", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(padx=20, pady=(25, 20), anchor="w")

        # --- CARD 1: File ---
        card_file = ctk.CTkFrame(sidebar)
        card_file.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(card_file, text="1. Seleziona Immagine", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.btn_browse = ctk.CTkButton(card_file, text="Sfoglia File...", command=self.browse_image)
        self.btn_browse.pack(padx=10, pady=5, fill="x")

        self.lbl_filename = ctk.CTkLabel(card_file, text="Nessun file selezionato", font=ctk.CTkFont(size=11), text_color="gray")
        self.lbl_filename.pack(padx=10, pady=(0, 10), anchor="w")
        
        # --- CARD 2: Dimensioni & Regolazioni ---
        card_settings = ctk.CTkFrame(sidebar)
        card_settings.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(card_settings, text="2. Impostazioni Pixel", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(10, 5), anchor="w")

        # Switch Proporzionale
        self.switch_prop = ctk.CTkSwitch(card_settings, text="Mantieni Proporzioni", command=self._on_switch_change)
        self.switch_prop.select()
        self.switch_prop.pack(padx=10, pady=(5, 15), anchor="w")

        # Griglia dinamica per Larghezza/Altezza o Lato Maggiore/Minore
        grid_frame = ctk.CTkFrame(card_settings, fg_color="transparent")
        grid_frame.pack(padx=10, pady=5, fill="x")
        grid_frame.columnconfigure(1, weight=1)

        self.lbl_main = ctk.CTkLabel(grid_frame, text="Lato Maggiore:", font=ctk.CTkFont(size=12))
        self.lbl_main.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.entry_main = ctk.CTkEntry(grid_frame, textvariable=self.str_dim_main, width=80)
        self.entry_main.grid(row=0, column=1, pady=5, sticky="we")

        self.lbl_sec = ctk.CTkLabel(grid_frame, text="Lato Minore (calc):", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_sec.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        self.entry_sec = ctk.CTkEntry(grid_frame, textvariable=self.str_dim_sec, width=80, state="disabled")
        self.entry_sec.grid(row=1, column=1, pady=5, sticky="we")
        
        # --- CARD 3: Azioni ---
        card_actions = ctk.CTkFrame(sidebar, fg_color="transparent")
        card_actions.pack(padx=15, pady=20, fill="x")
        
        self.btn_generate = ctk.CTkButton(card_actions, text="Genera Anteprima", font=ctk.CTkFont(weight="bold"), 
                                          fg_color="#1f538d", hover_color="#14375e", command=self.generate_preview)
        self.btn_generate.pack(pady=(0, 10), fill="x")

        self.btn_save = ctk.CTkButton(card_actions, text="Salva Pixel Art", font=ctk.CTkFont(weight="bold"), 
                                      fg_color="#27ae60", hover_color="#1e8449", command=self.save_image)
        self.btn_save.pack(pady=0, fill="x")

    # ------------------------------------------------------------------
    # 2. PANNELLO DI DESTRA (ANTEPRIME)
    # ------------------------------------------------------------------
    def _build_preview_area(self):
        preview_container = ctk.CTkFrame(self, fg_color="transparent")
        preview_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        preview_container.grid_columnconfigure((0, 1), weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        # Riquadro Originale
        frame_orig = ctk.CTkFrame(preview_container)
        frame_orig.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        ctk.CTkLabel(frame_orig, text="Originale", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.lbl_img_orig = ctk.CTkLabel(frame_orig, text="Carica un'immagine\nper iniziare", text_color="gray")
        self.lbl_img_orig.pack(expand=True, fill="both", padx=10, pady=10)

        # Riquadro Pixel Art
        frame_pixel = ctk.CTkFrame(preview_container)
        frame_pixel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        ctk.CTkLabel(frame_pixel, text="Risultato Pixel Art", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.lbl_img_pixel = ctk.CTkLabel(frame_pixel, text="Premi 'Genera Anteprima'\nper vedere il risultato", text_color="gray")
        self.lbl_img_pixel.pack(expand=True, fill="both", padx=10, pady=10)

    # ------------------------------------------------------------------
    # 3. LOGICA DI INTERAZIONE E TRANSIZIONE UI
    # ------------------------------------------------------------------
    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Immagini", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if not path:
            return

        self.input_path = path
        self.lbl_filename.configure(text=os.path.basename(path), text_color="white")

        with Image.open(path) as img:
            original_pil = img.convert("RGBA")
            # Mostra l'immagine originale mantenendo le proporzioni reali
            ctk_img = self._create_fitted_ctk_image(original_pil, max_size=280, is_pixel_art=False)
            self.lbl_img_orig.configure(image=ctk_img, text="")

        self._update_proportions()

    def _on_switch_change(self):
        """Modifica le etichette in base alla spunta delle proporzioni"""
        if self.switch_prop.get():
            # Modalità Intelligente (Proporzionale)
            self.lbl_main.configure(text="Lato lungo:")
            self.lbl_sec.configure(text="Lato corto (calc):", text_color="gray")
            self.entry_sec.configure(state="disabled")
            self._update_proportions()
        else:
            # Modalità Libera (No proporzioni)
            self.lbl_main.configure(text="Larghezza:")
            self.lbl_sec.configure(text="Altezza:", text_color=["gray10", "gray90"])
            self.entry_sec.configure(state="normal")

    def _update_proportions(self, *args):
        """Calcola automaticamente il lato minore se le proporzioni sono attive"""
        if not self.input_path or not self.switch_prop.get():
            return

        try:
            target_px = int(self.str_dim_main.get())
            if target_px > 0:
                # Usa logic.py per calcolare le dimensioni esatte mantenendo le proporzioni
                w, h = self.converter.get_proportional_dimensions(self.input_path, target_px)
                
                # Sblocca momentaneamente la seconda casella per aggiornare il valore
                self.entry_sec.configure(state="normal")
                self.str_dim_sec.set(str(min(w, h)))
                self.entry_sec.configure(state="disabled")
        except ValueError:
            pass 

    def generate_preview(self):
        if not self.input_path:
            messagebox.showwarning("Attenzione", "Seleziona prima un'immagine!")
            return

        try:
            if self.switch_prop.get():
                target_px = int(self.str_dim_main.get())
                w, h = self.converter.get_proportional_dimensions(self.input_path, target_px)
            else:
                w = int(self.str_dim_main.get())
                h = int(self.str_dim_sec.get())
                
            if w <= 0 or h <= 0: 
                raise ValueError
        except ValueError:
            messagebox.showwarning("Attenzione", "Inserisci valori validi numerici e maggiori di 0.")
            return

        with Image.open(self.input_path) as img:
            img = img.convert("RGBA")
            # 1. Crea l'effetto pixel art abbassando la risoluzione
            small_img = img.resize((w, h), Image.NEAREST)
            
            # 2. Mostra la Pixel Art ingrandendola con Image.NEAREST per mantenere i pixel netti (no sfocatura)
            ctk_preview = self._create_fitted_ctk_image(small_img, max_size=280, is_pixel_art=True)
            self.lbl_img_pixel.configure(image=ctk_preview, text="")

    def save_image(self):
        if not self.input_path:
            messagebox.showwarning("Attenzione", "Nessuna immagine da salvare.")
            return

        out_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")])
        if out_path:
            try:
                if self.switch_prop.get():
                    target_px = int(self.str_dim_main.get())
                    w, h = self.converter.get_proportional_dimensions(self.input_path, target_px)
                else:
                    w = int(self.str_dim_main.get())
                    h = int(self.str_dim_sec.get())

                self.converter.convert_to_pixel_art(self.input_path, out_path, w, h, export_scale=8)
                messagebox.showinfo("Successo", f"Pixel Art salvata con successo in:\n{out_path}")
            except Exception as e:
                messagebox.showwarning("Errore", str(e))

if __name__ == "__main__":
    converter = ImageToPixelArtConverter()
    app = PixelArtApp(converter)
    app.mainloop()