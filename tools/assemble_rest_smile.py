"""Reuse authored smile transitions on the accepted seated body; never redraw it."""
from pathlib import Path
import json
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
MOUTH = (83,93,95,99)


def assemble():
    folder = ROOT / "references/rest-smile/2026-10-23"
    base = Image.open(folder / "seated-base.png").convert("RGBA")
    donor = Image.open(folder / "smile-donor.png").convert("RGBA")
    assert base.size == donor.size == (768,288)
    frames = [base.crop((i%4*192,i//4*144,i%4*192+192,i//4*144+144)) for i in range(8)]
    frames += [frames[0].copy() for _ in range(4)]
    for index, source in ((5,4),(6,5),(7,5),(8,5),(9,4)):
        x,y = source%4*192,source//4*144
        patch = donor.crop(tuple(value+(x if n%2==0 else y) for n,value in enumerate(MOUTH)))
        patch.putalpha(frames[index].crop(MOUTH).getchannel("A"))
        frames[index].paste(patch,MOUTH[:2])
    sheet = Image.new("RGBA",(768,432))
    for index,frame in enumerate(frames):
        original = base.crop((index%4*192,index//4*144,index%4*192+192,index//4*144+144)) if index<8 else frames[0]
        for region in ((0,0,192,93),(0,99,192,144),(0,93,83,99),(95,93,192,99)):
            assert frame.crop(region).tobytes() == original.crop(region).tobytes(), (index,region)
        sheet.paste(frame,(index%4*192,index//4*144))
    sheet.save(ROOT / "assets/neko-idle-rest-v2.png")
    record = {"date":"2026-10-23","mode":"Reuse existing built-in ImageGen authored drawings; no new generation",
              "base":"references/rest-smile/2026-10-23/seated-base.png",
              "donor":"references/rest-smile/2026-10-23/smile-donor.png",
              "donor_provenance":"docs/rest-breathing-prompts.json",
              "mouth_region":MOUTH,"source_cells":{"half_smile":4,"small_smile":5},
              "selection":{"5":4,"6":5,"7":5,"8":5,"9":4},
              "acting":"Neutral first2.9s; drawn smile onset100ms, full smile2700ms, release100ms. Eye/ear/head/body acting remains pixel-identical at matching times. Mouth only; no breathing imported.",
              "spares":[10,11],"shared_neutral_alias":12,"canvas":[192,144]}
    (ROOT / "docs/rest-smile-assembly.json").write_text(json.dumps(record,indent=2),encoding="utf-8")


if __name__ == "__main__":
    assemble()
