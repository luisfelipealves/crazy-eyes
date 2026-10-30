"""Validate WFF1 structure, resolved images, AOD pixels and resource-only APK contract."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET
import zipfile
import tempfile
import xmlschema
from PIL import Image
from tools.watchface_preview import render_preview


def validate(root: Path, apk: Path | None = None):
    definition = root / 'watchface/src/main/res/raw/watchface.xml'
    with tempfile.TemporaryDirectory() as temporary:
        with zipfile.ZipFile(root / 'tools/wff-schema-v1.zip') as schemas:
            schemas.extractall(temporary)
        schema = xmlschema.XMLSchema11(Path(temporary) / 'watchface.xsd')
    schema.validate(definition)
    tree = ET.parse(definition)
    resources = definition.parent.parent / 'drawable-nodpi'
    referenced = {n.get('resource') for n in tree.iter() if n.get('resource')}
    decoded_bytes = 0
    for resource in referenced:
        paths = list(resources.glob(resource + '.*'))
        if len(paths) != 1: raise ValueError(f'Resource missing or ambiguous: {resource}')
        with Image.open(paths[0]) as im:
            decoded_bytes += im.width * im.height * 4 * getattr(im, 'n_frames', 1)
    if decoded_bytes > 100 * 1024 * 1024: raise ValueError('Interactive decoded image budget exceeded')
    ambient = render_preview(definition, ambient=True)
    lit = sum(ambient.convert('L').histogram()[1:]) / (ambient.width * ambient.height)
    if lit >= .15: raise ValueError(f'AOD illuminates {lit:.1%} of pixels')
    if ambient.crop((100, 0, 350, 85)).getbbox() is None: raise ValueError('AOD clock is hidden')
    if apk:
        with zipfile.ZipFile(apk) as archive:
            if any(n.endswith('.dex') or n.startswith('lib/') for n in archive.namelist()):
                raise ValueError('Watch face APK contains executable code')
            packaged = archive.read('res/raw/watchface.xml')
            schema.validate(packaged.decode())
    return dict(schema='WFF1', image_count=len(referenced), decoded_image_bytes=decoded_bytes,
                ambient_lit_percent=round(lit * 100, 2), apk_checked=bool(apk))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk', type=Path)
    args = parser.parse_args()
    print(validate(Path(__file__).resolve().parents[1], args.apk))
