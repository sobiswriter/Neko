"""Assemble authored seated support changes without torso breathing or contact drift."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, sprite_bounds, pet_landmarks
from tools.preview_idle_refresh import pixels
from tools.assemble_rest_blink import nose, EYES


def assemble():
    app=QApplication.instance() or QApplication([])
    atlas=SpriteAtlas(ROOT/'assets')
    canonical_q=atlas.frames['idle',0,0].toImage()
    canonical=pixels(atlas.frames['idle',0,0])
    bounds=sprite_bounds(canonical_q)
    _,head,_,_=pet_landmarks(canonical_q.copy(bounds))
    head+=bounds.left()
    path=ROOT/'docs/seated-idle-prompts.json'
    record=json.loads(path.read_text(encoding='utf-8'))
    raw=QImage(str(ROOT/record['selected_source']))
    assert not raw.isNull()
    poses,boxes=[],[]
    for index in range(8):
        l,r=(round((index%4+n)*raw.width()/4) for n in (0,1))
        t,b=(round((index//4+n)*raw.height()/2) for n in (0,1))
        cell=raw.copy(l,t,r-l,b-t)
        box=sprite_bounds(cell)
        assert not box.isEmpty()
        boxes.append([l+box.x(),t+box.y(),box.width(),box.height()])
        poses.append(cell.copy(box))
    width,ref_head,a,b=pet_landmarks(poses[0])
    sx,sy=62/width,82/poses[0].height()
    support=head+((a+b)/2-ref_head)*sx
    frames,registers=[canonical],[]
    for index in range(1,8):
        pose=poses[index]
        _,_,left,right=pet_landmarks(pose)
        q=pose.convertToFormat(QImage.Format_RGBA8888)
        drawing=Image.frombytes('RGBA',(q.width(),q.height()),bytes(q.constBits()))
        drawing=drawing.resize((round(drawing.width*sx),round(drawing.height*sy)),Image.Resampling.NEAREST)
        body_offset=(round(support-(left+right)/2*sx),130-drawing.height)
        body=Image.new('RGBA',canonical.size)
        body.paste(drawing,body_offset)
        frame=canonical.copy()
        torso=(78,100,119,120)
        frame.paste(body.crop(torso),torso[:2])
        center=nose(drawing)
        face_offset=tuple(round(a-b) for a,b in zip((86.5,90),center))
        face=Image.new('RGBA',canonical.size)
        face.paste(drawing,face_offset)
        for eye in EYES:
            patch=face.crop(eye)
            if index==3:
                patch=frames[2].crop(eye)
            patch.putalpha(canonical.crop(eye).getchannel('A'))
            frame.paste(patch,eye[:2])
        if index==1:
            ear=(59,46,82,73)
            frame.paste(face.crop(ear),ear[:2])
        assert frame.crop((0,120,192,144)).tobytes()==canonical.crop((0,120,192,144)).tobytes()
        assert frame.crop((119,98,192,144)).tobytes()==canonical.crop((119,98,192,144)).tobytes()
        frames.append(frame)
        registers.append({'source':index,'support_offset':body_offset,'face_offset':face_offset})
    sheet=Image.new('RGBA',(768,288))
    keys=Image.new('RGB',(768,350),'#f8f5ee')
    draw=ImageDraw.Draw(keys)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    for index,frame in enumerate(frames):
        sheet.paste(frame,(index%4*192,index//4*144))
        keys.paste(frame,(index%4*192,index//4*175),frame)
        draw.text((index%4*192+10,index//4*175+147),str(index),font=font,fill='#6c6259')
    folder=ROOT/'build/seated-idle'
    folder.mkdir(parents=True,exist_ok=True)
    sheet.save(folder/'rest-candidate.png')
    keys.save(folder/'rest-candidate-keys.png')
    record['assembly']={'source_boxes':boxes,'batch_scale':[sx,sy],'support_target':support,
                        'registration':registers,'torso_foreleg_region':[78,100,119,120],
                        'contact_lock_y':120,'quiet_tail_lock_x':119,
                        'eyes':EYES,'ear_region':[59,46,82,73],
                        'output':'assets/neko-idle-rest-v2.png',
                        'method':'Whole authored torso/foreleg poses over exact planted contacts, stable head scaffold with authored eye/ear acting. No chest-only shading window, no breathing/scaling, no global animated translation.'}
    path.write_text(json.dumps(record,indent=2),encoding='utf-8')


if __name__=='__main__':
    assemble()
