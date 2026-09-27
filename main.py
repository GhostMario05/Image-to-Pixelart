from logic import ImageToPixelArtConverter
from ui import PixelArtApp

def main():
    converter = ImageToPixelArtConverter()
    app = PixelArtApp(converter)
    app.mainloop()

if __name__ == "__main__":
    main()