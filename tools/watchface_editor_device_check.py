"""Capture the real stock editor; screenshots still require visual inspection."""
import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from PIL import Image

NAMES={'calm':'calm','tranquilo':'calm','crazy':'crazy','maluco':'crazy'}

def bounds(node):
    points=[int(v) for v in re.findall(r'\d+',node.get('bounds',''))]
    return points if len(points)==4 else (0,0,0,0)


def visible_intensity_labels(xml):
    found=set()
    for node in ET.fromstring(xml).iter('node'):
        x1,y1,x2,y2=bounds(node)
        if x2<=x1 or y2<=y1 or x1>=450 or y1>=450 or x2<=0 or y2<=0:continue
        for key in ('text','content-desc'):
            label=node.get(key,'').split(',')[0].strip().casefold()
            if label in NAMES:found.add(NAMES[label])
    return found


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    def adb(*args):return subprocess.check_output(['adb',*args],timeout=30)
    def snapshot(label):
        adb('shell','uiautomator','dump','/sdcard/crazy-eyes-editor.xml')
        xml=adb('exec-out','cat','/sdcard/crazy-eyes-editor.xml').decode()
        (output/(label+'.xml')).write_text(xml)
        Image.open(io.BytesIO(adb('exec-out','screencap','-p'))).save(output/(label+'.png'))
        return xml,ET.fromstring(xml)
    def tap_named(root, predicate):
        for node in root.iter('node'):
            names=[node.get(k,'').strip().casefold() for k in ('text','content-desc')]
            if any(predicate(name) for name in names):
                x1,y1,x2,y2=bounds(node)
                if x2>x1 and y2>y1 and 0<=(x1+x2)//2<450 and 0<=(y1+y2)//2<450:
                    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2));return True
        return False
    try:
        adb('shell','input','swipe','225','225','225','225','1500')
        time.sleep(.7)
        xml,root=snapshot('picker')
        labels=' '.join(n.get('text','') for n in root.iter('node')).casefold()
        if not any(t in labels for t in ('eye style','iris color','animation intensity','intensidade das animações')):
            if not tap_named(root,lambda s:s in ('edit','customize','personalizar','editar') or any(s.startswith(prefix) for prefix in ('customize ','edit ','personalizar ','editar '))):
                raise AssertionError('Native picker has no named Customize/Edit action; inspect picker.png/xml')
            time.sleep(.7)
        seen=set();opened=False
        swipes=[('225','350','225','100'),('225','350','225','100'),('350','225','95','225'),('350','225','95','225'),('95','225','350','225'),('225','110','225','350')]
        for i in range(12):
            xml,root=snapshot(f'editor-{i}')
            seen|=visible_intensity_labels(xml)
            (output/'labels.json').write_text(json.dumps({'visible_options':sorted(seen)}))
            if seen=={'calm','crazy'}:
                print('PASS native editor: Calm and Crazy option names exposed; inspect captioned icon screenshots',flush=True)
                return
            if not opened and tap_named(root,lambda s:any(s.startswith(prefix) for prefix in ('animation intensity','intensidade das animações'))):
                opened=True
            else:
                adb('shell','input','swipe',*swipes[i%len(swipes)],'350')
            time.sleep(.5)
        raise AssertionError(f'Native editor did not expose both intensity options: {seen}; inspect captures')
    finally:
        (output/'logcat.txt').write_bytes(adb('logcat','-d','-v','brief'))
        (output/'windows.txt').write_bytes(adb('shell','dumpsys','window'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
