from PIL import Image

class ImageToPixelArtConverter:
    def __init__(self):
        pass

    def convert_to_pixel_art(self, image_path, output_path, width, height, export_scale=8):
        """
        Converte l'immagine in Pixel Art e la salva su disco.
        
        :param export_scale: Ingrandisce il risultato finale per renderlo visibile su schermo (default 8x).
        """
        with Image.open(image_path) as img:
            # Converte in RGBA per gestire in modo sicuro sia PNG trasparenti che JPG
            img = img.convert("RGBA")
            
            # 1. Ridimensiona verso il basso (crea l'effetto pixel art)
            small_img = img.resize((width, height), Image.NEAREST)
            
            # 2. Ingrandisce l'immagine per l'export (altrimenti sarebbe microscopica)
            if export_scale > 1:
                final_w = width * export_scale
                final_h = height * export_scale
                final_img = small_img.resize((final_w, final_h), Image.NEAREST)
            else:
                final_img = small_img
            
            # Se la salvi come JPG, la riconvertiamo in RGB (JPG non supporta la trasparenza)
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                final_img = final_img.convert("RGB")

            # Salva l'immagine finale
            final_img.save(output_path)
            print(f"Pixel art salvata con successo in: {output_path}")

    def get_proportional_dimensions(self, image_path, target_pixels):
        """
        Calcola le nuove dimensioni (width, height) mantenendo le proporzioni originali.
        Ritorna una tupla (new_width, new_height) pronta per essere usata dalla UI.
        """
        with Image.open(image_path) as img:
            width, height = img.size
            
            if width > height:
                new_width = target_pixels
                new_height = max(1, int(height * (target_pixels / width)))
            else:
                new_height = target_pixels
                new_width = max(1, int(width * (target_pixels / height)))
                
            return new_width, new_height