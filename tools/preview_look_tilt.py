"""Compare original looks with restored updated looks and authored tilted smiles."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtWidgets import QApplication
from animations import CLIPS, SpriteAtlas
from tools.preview_idle_stability import frozen
from tools.preview_idle_refresh import pixels, displayed


def preview(before):
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT/"assets")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",14)
    with tempfile.TemporaryDirectory() as folder:
        previous, old = frozen(before,folder,"original_directional_looks")
        retained = [key for key in old.frames if key[0] != "idleplay-c"]
        assert all(old.frames[key].toImage() == atlas.frames[key].toImage() for key in retained)
        unchanged = [name for name in CLIPS if name not in ("look_left","look_right")]
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unchanged)
        for name in ("look_left","look_right"):
            frames=[]
            for index in range(112):
                canvas=Image.new("RGB",(480,222),"#f8f5ee")
                draw=ImageDraw.Draw(canvas)
                draw.text((16,10),"ORIGINAL",font=font,fill="#6c6259")
                draw.text((256,10),"UPDATED + HAPPY TILT",font=font,fill="#6c6259")
                for col,(source,clips,legacy) in enumerate(((old,previous.CLIPS,True),(atlas,CLIPS,False))):
                    frame=displayed(source,clips,name,index/10,legacy)
                    canvas.paste(frame,(24+col*240,36),frame)
                draw.text((16,195),name.replace('_',' ').title()+" | native size, normal speed",font=font,fill="#6c6259")
                frames.append(canvas)
            frames[0].save(ROOT/f"docs/look-tilt-{name}.gif",save_all=True,append_images=frames[1:],duration=100,loop=0,disposal=2)
    sheet=Image.new("RGB",(768,350),"#f8f5ee")
    draw=ImageDraw.Draw(sheet)
    for n,index in enumerate(range(16,24)):
        frame=pixels(atlas.frames["idle-v2-look",index//4,index%4])
        x,y=n%4*192,n//4*175
        sheet.paste(frame,(x,y),frame)
        draw.text((x+12,y+147),str(index)+" / "+("Tilt","Smile","Happy hold","Recover")[n%4],font=font,fill="#6c6259")
    sheet.save(ROOT/"docs/look-tilt-frames.png")
    sizes=[]
    for index in range(16,24):
        frame=pixels(atlas.frames["idle-v2-look",index//4,index%4])
        alpha=frame.getchannel("A")
        opaque={(x,y) for y in range(144) for x in range(192) if alpha.getpixel((x,y))>=128}
        components=[]
        while opaque:
            pending=[opaque.pop()]
            count=0
            while pending:
                x,y=pending.pop()
                count+=1
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                    point=x+dx,y+dy
                    if point in opaque:
                        opaque.remove(point)
                        pending.append(point)
            components.append(count)
        assert sum(n>2 for n in components)==1,(index,components)
        sizes.append(components)
    result={"atlas_entries":len(atlas.frames),"unchanged_frames":len(retained),"unchanged_clips":unchanged,
            "look_duration_ms":sum(CLIPS['look_left'].durations),"happy_hold_ms":600,
            "new_source_components":sizes,"updated_glance_source_cells_preserved":16}
    assert len(atlas.frames)==904 and len(retained)==879 and len(unchanged)==63
    (ROOT/"docs/look-tilt-metrics.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    (ROOT/"docs/look-tilt-compare.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko happy tilted looks</title><style>body{background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:850px;margin:32px auto;padding:0 16px}img{max-width:100%;image-rendering:pixelated}p{line-height:1.6}</style><main><h1>A little look, a happy little tilt.</h1><p>Original on the left, updated glance with the new tilted smile on the right. Native desktop size and normal speed. Both directions get their own drawn tilt; her seated body and tail stay planted.</p><h2>Look left</h2><img width="480" height="222" src="look-tilt-look_left.gif" alt="Original and updated left look with happy tilt"><h2>Look right</h2><img width="480" height="222" src="look-tilt-look_right.gif" alt="Original and updated right look with happy tilt"><p>The pleased tilt holds600ms, then she straightens through drawn poses. Each gesture runs4.9s once; these previews repeat for review.</p><img width="768" height="350" src="look-tilt-frames.png" alt="Drawn tilt, smile, happy hold and recovery poses in both directions"><p>Resting breathing, original quiet tail swish and tail chase/catch are unchanged.</p><a href="look-tilt-validation.md">Sources, checks and remaining limits</a></main></html>''',encoding="utf-8")
    print(json.dumps(result))


if __name__=="__main__":
    preview(Path(sys.argv[1]))
