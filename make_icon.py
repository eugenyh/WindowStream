"""Draws icon.ico for the exe: a green circle with a \"play\" triangle (like the tray icon)."""
from PIL import Image, ImageDraw


def draw(size):
    k = size / 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2 * k, 2 * k, 62 * k, 62 * k), fill=(40, 170, 70))
    d.polygon([(24 * k, 16 * k), (24 * k, 48 * k), (50 * k, 32 * k)], fill=(255, 255, 255))
    return img


if __name__ == "__main__":
    base = draw(256)
    base.save("icon.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    print("icon.ico created")
