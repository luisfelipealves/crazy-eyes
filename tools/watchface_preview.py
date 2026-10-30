"""Layout preview for this WFF subset; the Wear OS renderer still requires device testing."""
from pathlib import Path
import argparse
import ast
import math
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops, ImageDraw, ImageFont

DEFAULTS = dict(IS_24_HOUR_MODE=True, HOUR_0_23_Z='10', HOUR_1_12=10, MINUTE_Z='08',
                ACCELEROMETER_IS_SUPPORTED=True, ACCELEROMETER_ANGLE_X=0,
                ACCELEROMETER_ANGLE_Y=0, SECONDS_IN_DAY=10, SECOND_MILLISECOND=1)
FUNCTIONS = dict(abs=abs, floor=math.floor, sin=math.sin,
                 fract=lambda x: x - math.floor(x), clamp=lambda x, low, high: max(low, min(x, high)))


def evaluate(expression, values):
    source = re.sub(r'\[([A-Z_0-9]+)\]', r'\1', expression)
    tree = ast.parse(source, mode='eval')
    allowed = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Call, ast.BinOp,
               ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub, ast.UAdd)
    for node in ast.walk(tree):
        if not isinstance(node, allowed): raise ValueError(f'Unsupported expression: {expression}')
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS):
            raise ValueError('Unsupported function')
    return eval(compile(tree, '<wff-expression>', 'eval'), {'__builtins__': {}}, FUNCTIONS | values)


def render_preview(xml_path: Path, ambient=False, values=None, poke=None):
    root = ET.parse(xml_path).getroot()
    resources = xml_path.parent.parent / 'drawable-nodpi'
    data = DEFAULTS | (values or {})
    canvas_size = (int(root.get('width')), int(root.get('height')))

    def image_resource(name, frame=0):
        files = list(resources.glob(name + '.*'))
        if not files: raise ValueError(f'Missing image {name}')
        with Image.open(files[0]) as im:
            im.seek(frame)
            return im.convert('RGBA')

    def selected_children(node, env):
        for child in node:
            if child.tag == 'Condition':
                local = env.copy()
                for expression in child.find('Expressions'):
                    local[expression.get('name')] = evaluate(expression.text, local)
                branch = next((c for c in child.findall('Compare') if evaluate(c.get('expression'), local)), child.find('Default'))
                if branch is not None: yield from selected_children(branch, local)
            elif child.tag not in ('Expressions', 'Variant', 'Transform', 'Gyro'):
                yield child, env

    def part_text(node, env):
        out = Image.new('RGBA', canvas_size)
        circle = node.find('TextCircular')
        font_node = circle.find('Font')
        size = int(font_node.get('size'))
        font = ImageFont.truetype('DejaVuSans.ttf', size)
        template = font_node.find('Template')
        text = (template.text or '') % tuple(evaluate(p.get('expression'), env) for p in template)
        radius = float(circle.get('width')) / 2 - size / 2
        cx, cy = float(circle.get('centerX')), float(circle.get('centerY'))
        widths = [font.getlength(c) for c in text]
        position = -sum(widths) / 2
        for char, advance in zip(text, widths):
            angle = (position + advance / 2) / radius
            tile = Image.new('RGBA', (size * 3, size * 3))
            ImageDraw.Draw(tile).text((size * 1.5, size * 1.5), char, font=font,
                                     fill=font_node.get('color'), anchor='mm')
            tile = tile.rotate(-math.degrees(angle), resample=Image.Resampling.BICUBIC)
            out.alpha_composite(tile, (round(cx + radius * math.sin(angle) - tile.width / 2),
                                       round(cy - radius * math.cos(angle) - tile.height / 2)))
            position += advance
        return out

    def render(node, env):
        width, height = int(node.get('width', 450)), int(node.get('height', 450))
        attrs = dict(node.attrib)
        if ambient:
            for variant in node.findall('Variant'):
                attrs[variant.get('target')] = variant.get('value')
        for transform in node.findall('Transform'):
            attrs[transform.get('target')] = evaluate(transform.get('value'), env)
        gyro = node.find('Gyro')
        if gyro is not None:
            for key, value in gyro.attrib.items(): attrs[key] = float(attrs.get(key, 0)) + evaluate(value, env)
        layer = Image.new('RGBA', (width, height))
        if node.tag in ('Scene', 'Group'):
            masks = []
            for child, child_env in selected_children(node, env):
                painted, x, y = render(child, child_env)
                if child.get('renderMode') == 'MASK':
                    field = Image.new('RGBA', (width, height)); field.alpha_composite(painted, (x, y)); masks.append(field.getchannel('A'))
                else: layer.alpha_composite(painted, (x, y))
            for mask in masks: layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))
        elif node.tag in ('PartImage', 'PartAnimatedImage'):
            resource = node.find('Image') if node.tag == 'PartImage' else node.find('Thumbnail')
            if poke and node.get('name') == poke[0]:
                img = image_resource(node.find('AnimatedImage').get('resource'), poke[1])
            else: img = image_resource(resource.get('resource'))
            layer = img.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
        elif node.tag == 'PartText': layer = part_text(node, env)
        alpha = float(attrs.get('alpha', 255)) / 255
        if alpha != 1: layer.putalpha(layer.getchannel('A').point(lambda p: round(p * alpha)))
        sy = float(attrs.get('scaleY', 1))
        if sy != 1:
            squashed = layer.resize((width, max(1, round(height * sy))), Image.Resampling.LANCZOS)
            layer = Image.new('RGBA', (width, height))
            layer.alpha_composite(squashed, (0, (height - squashed.height) // 2))
        return layer, round(float(attrs.get('x', 0))), round(float(attrs.get('y', 0)))

    foreground, _, _ = render(root.find('Scene'), data)
    result = Image.new('RGBA', canvas_size, 'black'); result.alpha_composite(foreground)
    return result.convert('RGB')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('xml', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--ambient', action='store_true')
    args = parser.parse_args()
    render_preview(args.xml, args.ambient).save(args.output)
