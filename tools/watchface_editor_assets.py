"""Deterministic, tint-safe captions for image-based watch face editors."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def option_icon(mode, caption):
    image=Image.new('RGBA',(400,400));draw=ImageDraw.Draw(image)
    for x in (130,270):
        draw.ellipse((x-46,75,x+46,230),fill='white')
        if mode=='calm':
            draw.rectangle((x-48,70,x+48,147),fill=(0,0,0,0))
            px,py=x,184
        else:
            px,py=x+(13 if x==130 else -13),140 if x==130 else 185
        draw.ellipse((px-23,py-23,px+23,py+23),fill=(0,0,0,0))
        draw.ellipse((px-10,py-10,px-1,py-1),fill='white')
    if mode=='crazy':
        for x in (62,338):draw.line([(x,125),(x-10,145),(x+4,145),(x-7,166)],fill='white',width=5)
    size=58
    font=ImageFont.truetype('DejaVuSans-Bold.ttf',size)
    while font.getlength(caption)>320:
        size-=1;font=ImageFont.truetype('DejaVuSans-Bold.ttf',size)
    draw.text((200,280),caption,font=font,fill='white',anchor='mt')
    return image


def generate(res):
    for folder,captions in [('drawable-nodpi',{'calm':'Calm','crazy':'Crazy'}),
                            ('drawable-pt-nodpi',{'calm':'Tranquilo','crazy':'Maluco'})]:
        target=res/folder;target.mkdir(parents=True,exist_ok=True)
        for mode,caption in captions.items():option_icon(mode,caption).save(target/f'intensity_{mode}_icon.png')


if __name__=='__main__':generate(Path(__file__).resolve().parents[1]/'watchface/src/main/res')
