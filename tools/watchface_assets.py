"""Reproducible bitmap resources for the resource-only WFF watch face."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw

SIZE = 450
EYE_WIDTH, EYE_HEIGHT = 153, 207
EYE_POSITIONS = ((54, 122), (243, 122))


def mask(openness=1.0):
    scale = 3
    im = Image.new('RGBA', (EYE_WIDTH * scale, EYE_HEIGHT * scale))
    half = EYE_HEIGHT * openness / 2
    ImageDraw.Draw(im).ellipse((0, (EYE_HEIGHT / 2 - half) * scale,
                               EYE_WIDTH * scale - 1, (EYE_HEIGHT / 2 + half) * scale - 1),
                              fill='white')
    return im.resize((EYE_WIDTH, EYE_HEIGHT), Image.Resampling.LANCZOS)


def generate(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    mask().save(output / 'eye_mask.png')
    sclera = Image.new('RGB', (EYE_WIDTH, EYE_HEIGHT))
    pixels = sclera.load()
    for y in range(EYE_HEIGHT):
        for x in range(EYE_WIDTH):
            amount = .75 * y / EYE_HEIGHT + .25 * x / EYE_WIDTH
            pixels[x, y] = tuple(round(255 + (end - 255) * amount) for end in (222, 231, 240))
    sclera.save(output / 'sclera.png')
    pupil = Image.new('RGBA', (216, 216))
    draw = ImageDraw.Draw(pupil)
    draw.ellipse((1, 1, 215, 215), fill=(44, 51, 63))
    draw.ellipse((25, 25, 191, 191), fill=(6, 8, 13))
    draw.ellipse((60, 53, 96, 89), fill='white')
    draw.ellipse((133, 134, 149, 150), fill=(255, 255, 255, 160))
    pupil.resize((72, 72), Image.Resampling.LANCZOS).save(output / 'pupil.png')
    frames = []
    for i in range(18):
        t = i / 17
        recovery = max(0.0, (t - .14) / .86)
        openness = .06 + .94 * (1 - (1 - recovery) ** 2)
        frames.append(mask(openness))
    frames[-1] = mask()
    frames[0].save(output / 'poke_mask.webp', save_all=True, append_images=frames[1:],
                   duration=50, loop=1, lossless=True, minimize_size=True)
    ambient = Image.new('RGB', (SIZE * 3, SIZE * 3), 'black')
    draw = ImageDraw.Draw(ambient)
    for x, y in EYE_POSITIONS:
        draw.ellipse((x * 3, y * 3, (x + EYE_WIDTH) * 3 - 1, (y + EYE_HEIGHT) * 3 - 1),
                     outline=(112, 119, 128), width=6)
    ambient.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(output / 'eyes_ambient.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    generate(parser.parse_args().output)
