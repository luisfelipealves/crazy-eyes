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
                ACCELEROMETER_ANGLE_Y=0, ACCELEROMETER_X=0, ACCELEROMETER_Y=0,
                ACCELEROMETER_Z=9.8, SECONDS_IN_DAY=10, SECOND_MILLISECOND=1,
                BATTERY_PERCENT=100, BATTERY_CHARGING_STATUS=False)
FUNCTIONS = dict(abs=abs, floor=math.floor, sin=math.sin,
                 fract=lambda x: x - math.floor(x), clamp=lambda x, low, high: max(low, min(x, high)))


def evaluate(expression, values):
    source = re.sub(r'\[([A-Za-z_0-9.]+)\]', lambda m: m[1].replace('.', '__'), expression)
    source = re.sub(r'!(?!=)', ' not ', source.replace('&&', ' and ').replace('||', ' or ')).strip()
    if '?' in source:
        condition, branches = source.split('?', 1)
        yes, no = branches.split(':', 1)
        source = f'({yes}) if ({condition}) else ({no})'
    tree = ast.parse(source, mode='eval')
    allowed = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Call, ast.BinOp,
               ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub, ast.UAdd,
               ast.IfExp, ast.Compare, ast.Eq, ast.Gt, ast.LtE, ast.BoolOp, ast.And, ast.Or, ast.Not)
    for node in ast.walk(tree):
        if not isinstance(node, allowed): raise ValueError(f'Unsupported expression: {expression}')
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS):
            raise ValueError('Unsupported function')
    return eval(compile(tree, '<wff-expression>', 'eval'), {'__builtins__': {}}, FUNCTIONS | {k.replace('.', '__'): v for k, v in values.items()})


def render_preview(xml_path: Path, ambient=False, values=None, poke=None):
    root = ET.parse(xml_path).getroot()
    resources = xml_path.parent.parent / 'drawable-nodpi'
    data = DEFAULTS | (values or {})
    configurations = root.find('UserConfigurations')
    if configurations is not None:
        for configuration in configurations:
            key = 'CONFIGURATION.' + configuration.get('id')
            choice = data.setdefault(key, configuration.get('defaultValue'))
            if configuration.tag == 'BooleanConfiguration':
                if choice not in ('TRUE', 'FALSE'):
                    raise ValueError(f'Unknown configuration {key}={choice}')
                continue
            option = next((o for o in configuration if o.get('id') == choice), None)
            if option is None:
                raise ValueError(f'Unknown configuration {key}={choice}')
            if configuration.tag == 'ColorConfiguration':
                for i, color in enumerate(option.get('colors').split()):
                    data[f'{key}.{i}'] = color
    canvas_size = (int(root.get('width')), int(root.get('height')))

    def image_resource(name, frame=0):
        files = list(resources.glob(name + '.*'))
        if not files: raise ValueError(f'Missing image {name}')
        with Image.open(files[0]) as im:
            im.seek(frame)
            return im.convert('RGBA')

    def selected_children(node, env):
        for child in node:
            if child.tag == 'ListConfiguration':
                choice = env['CONFIGURATION.' + child.get('id')]
                option = next(o for o in child if o.get('id') == choice)
                yield from selected_children(option, env)
            elif child.tag == 'Condition':
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
        family = font_node.get('family')
        font_path = resources.parent / 'font' / (family + '.ttf')
        font = ImageFont.truetype(str(font_path) if font_path.exists() else 'DejaVuSans.ttf', size)
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
                                     fill=(env[font_node.get('color')[1:-1]] if font_node.get('color', '').startswith('[') else font_node.get('color')), anchor='mm')
            tile = tile.rotate(-math.degrees(angle), resample=Image.Resampling.BICUBIC)
            out.alpha_composite(tile, (round(cx + radius * math.sin(angle) - tile.width / 2),
                                       round(cy - radius * math.cos(angle) - tile.height / 2)))
            position += advance
        return out

    def part_draw(node, env, width, height):
        # Supersampling approximates native vector AA; it does not simulate timing.
        scale = 3
        out = Image.new('RGBA', (width * scale, height * scale))
        for shape in node:
            if shape.tag in ('Transform', 'Variant', 'Gyro'):
                continue
            fill = shape.find('Fill')
            color = fill.get('color')
            if color.startswith('['):
                color = env[color[1:-1]]
            if len(color) == 9:  # WFF uses ARGB, Pillow uses RGBA.
                color = color[0] + color[3:] + color[1:3]
            x, y, w, h = (float(shape.get(k)) * scale for k in ('x', 'y', 'width', 'height'))
            overlay = Image.new('RGBA', out.size)
            draw = ImageDraw.Draw(overlay)
            bounds = (x, y, x + w, y + h)
            if shape.tag == 'Ellipse':
                draw.ellipse(bounds, fill=color)
            elif shape.tag == 'RoundRectangle':
                draw.rounded_rectangle(bounds, radius=float(shape.get('cornerRadiusX')) * scale, fill=color)
            elif shape.tag == 'Rectangle':
                draw.rectangle(bounds, fill=color)
            else:
                raise ValueError(f'Unsupported draw shape: {shape.tag}')
            out.alpha_composite(overlay)
        return out.resize((width, height), Image.Resampling.LANCZOS)

    def render(node, env):
        width, height = int(node.get('width', 450)), int(node.get('height', 450))
        attrs = dict(node.attrib)
        if ambient:
            for variant in node.findall('Variant'):
                attrs[variant.get('target')] = variant.get('value')
        for transform in node.findall('Transform'):
            target = transform.get('target')
            value = evaluate(transform.get('value'), env)
            # Wear OS4 applies transformed pivots in scene units, whereas
            # static pivot attributes are normalized. Keep the latter form
            # internally so the rotation math below handles both correctly.
            if target == 'pivotX': value /= width
            if target == 'pivotY': value /= height
            attrs[target] = value
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
            if masks:
                # WFF combines sibling masks on one canvas (union), not as
                # successive intersections. Intersections require nested groups.
                combined = Image.new('L', (width, height))
                for mask in masks: combined = ImageChops.screen(combined, mask)
                layer.putalpha(ImageChops.multiply(layer.getchannel('A'), combined))
        elif node.tag in ('PartImage', 'PartAnimatedImage'):
            resource = node.find('Image') if node.tag == 'PartImage' else node.find('Thumbnail')
            if poke and node.get('name') == poke[0]:
                img = image_resource(node.find('AnimatedImage').get('resource'), poke[1])
            else: img = image_resource(resource.get('resource'))
            layer = img.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
        elif node.tag == 'PartDraw': layer = part_draw(node, env, width, height)
        elif node.tag == 'PartText': layer = part_text(node, env)
        alpha = float(attrs.get('alpha', 255)) / 255
        if alpha != 1: layer.putalpha(layer.getchannel('A').point(lambda p: round(p * alpha)))
        sx, sy = float(attrs.get('scaleX', 1)), float(attrs.get('scaleY', 1))
        if sx != 1 or sy != 1:
            squashed = layer.resize((max(1, round(width * sx)), max(1, round(height * sy))), Image.Resampling.LANCZOS)
            layer = Image.new('RGBA', (width, height))
            layer.alpha_composite(squashed, ((width - squashed.width) // 2, (height - squashed.height) // 2))
        x, y = round(float(attrs.get('x', 0))), round(float(attrs.get('y', 0)))
        angle = float(attrs.get('angle', 0))
        if angle:
            # Only the current angle is drawn. This is not a temporal WFF simulator.
            px = float(attrs.get('pivotX', .5)) * width
            py = float(attrs.get('pivotY', .5)) * height
            c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            corners = [(c * (a - px) - s * (b - py) + px,
                        s * (a - px) + c * (b - py) + py)
                       for a, b in ((0, 0), (width, 0), (0, height), (width, height))]
            left = math.floor(min(p[0] for p in corners))
            top = math.floor(min(p[1] for p in corners))
            right = math.ceil(max(p[0] for p in corners))
            bottom = math.ceil(max(p[1] for p in corners))
            layer = layer.transform((right - left, bottom - top), Image.Transform.AFFINE,
                                    (c, s, c * (left - px) + s * (top - py) + px,
                                     -s, c, -s * (left - px) + c * (top - py) + py),
                                    resample=Image.Resampling.BICUBIC)
            x += left
            y += top
        return layer, x, y

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
