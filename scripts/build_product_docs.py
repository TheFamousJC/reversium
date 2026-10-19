"""Build public feature and journey assets from one reviewed catalog. No user data."""
import hashlib
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reversium import __version__
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

CATALOG = ROOT / 'docs/product-catalog.json'


def asset_hash(path):
    data=path.read_bytes()
    if path.suffix in ('.json','.html','.svg'):data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def journey_svg(journey):
    esc = html.escape
    # Four vertical steps keep both long labels and the reading order legible.
    ident=journey['id']
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="720" viewBox="0 0 760 720" role="img" aria-labelledby="'+ident+'-title '+ident+'-desc">',
             '<title id="'+ident+'-title">'+esc(journey['title'])+'</title>',
             '<desc id="'+ident+'-desc">'+esc(' Then '.join(' - '.join(x) for x in journey['steps']))+'</desc>',
             '<rect width="760" height="720" fill="#f5f7ff"/>']
    for i, (label, detail) in enumerate(journey['steps']):
        y = 25+i*172
        parts += [f'<rect x="25" y="{y}" width="710" height="126" rx="16" fill="white" stroke="#c4cfe6"/>',
                  f'<circle cx="65" cy="{y+42}" r="22" fill="#4058da"/>',
                  f'<text x="65" y="{y+49}" text-anchor="middle" fill="white" font-family="sans-serif" font-size="20">{i+1}</text>',
                  f'<text x="105" y="{y+45}" fill="#17253c" font-family="sans-serif" font-size="23" font-weight="bold">{esc(label)}</text>']
        # Explicit line wrapping, rather than tiny text or SVG foreignObject.
        words=detail.split(); lines=['']
        for word in words:
            if len(lines[-1])+len(word)>61:lines.append(word)
            else:lines[-1]+=(' ' if lines[-1] else '')+word
        for n,line in enumerate(lines):
            parts.append(f'<text x="105" y="{y+79+n*25}" fill="#465570" font-family="sans-serif" font-size="19">{esc(line)}</text>')
        if i<3:
            parts.append(f'<path d="M380 {y+135} v22 m-8 -8 l8 8 8 -8" fill="none" stroke="#4058da" stroke-width="3"/>')
    return ''.join(parts)+'</svg>'


def journeys_section(data):
    esc=html.escape
    cards=[]
    for i,j in enumerate(data['journeys'],1):
        steps='<ol class="journey-steps" aria-label="'+esc(j['title'])+'">'+''.join('<li><span class="journey-number" aria-hidden="true">'+str(n)+'</span><div><strong>'+esc(label)+'</strong><span>'+esc(detail)+'</span></div></li>' for n,(label,detail) in enumerate(j['steps'],1))+'</ol>'
        cards.append('<article class="journey"><h3>'+str(i)+'. '+esc(j['title'])+'</h3><p><b>'+esc(j['who'])+'</b> - '+esc(j['goal'])+'</p>'+steps+'<p><b>Take away:</b> '+esc(j['output'])+'</p><p><b>Boundary:</b> '+esc(j['limit'])+'</p></article>')
    return '<style>.journey{margin:28px 0;padding:24px;min-width:0;background:#fff;color:#17253c;border:1px solid #c4cfe6;border-radius:12px}.journey h3{color:#17253c;font-size:21px}.journey p{line-height:1.6;color:#465570}.journey-steps{list-style:none;padding:0;margin:20px auto;max-width:650px}.journey-steps li{position:relative;display:flex;gap:16px;padding:18px;border:1px solid #c4cfe6;border-radius:12px;background:#fff;color:#17253c;margin-bottom:32px}.journey-steps li:not(:last-child):after{content:"↓";position:absolute;left:50%;bottom:-29px;color:#4058da;font-size:24px;line-height:28px}.journey-number{display:flex;align-items:center;justify-content:center;flex:0 0 34px;height:34px;border-radius:50%;background:#4058da;color:#fff}.journey-steps strong,.journey-steps span:not(.journey-number){display:block;overflow-wrap:anywhere}.journey-steps strong{color:#17253c;font-size:18px;margin-bottom:8px}.journey-steps div>span{color:#465570;font-size:16px;line-height:1.5}</style>'+''.join(cards)


def build():
    data=json.loads(CATALOG.read_text(encoding='utf-8'))
    if len(data['journeys'])!=7:raise ValueError('Exactly seven user journeys are required.')
    out=ROOT/'output/pdf';out.mkdir(parents=True,exist_ok=True)
    diagrams=ROOT/'docs/journeys';diagrams.mkdir(exist_ok=True)
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=10;styles['BodyText'].leading=14;styles['BodyText'].spaceAfter=7
    styles['Heading2'].textColor=colors.HexColor('#4058da')
    esc=html.escape
    def footer(c,d):
        c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#465570'))
        c.drawString(18*mm,12*mm,'3Sci Labs / '+data['reviewed_on']+' / Build '+__version__)
        c.drawRightString(192*mm,12*mm,str(d.page))
    story=[]
    for i,g in enumerate(data['feature_groups']):
        if i:story.append(PageBreak())
        story += [Paragraph('Reversium by 3Sci Labs',styles['Title']),Paragraph('Feature list / Build '+__version__+' / '+data['reviewed_on'],styles['BodyText']),Paragraph(esc(g['title']),styles['Heading1'])]
        for f in g['features']:
            story.append(KeepTogether([Paragraph(esc(f['name'])+' <font size="9" color="#465570"> / '+esc(f['availability'])+'</font>',styles['Heading2']),Paragraph(esc(f['does']),styles['BodyText']),Paragraph('<b>Limit:</b> '+esc(f['limit']),styles['BodyText'])]))
    feature=out/'Reversium-Feature-List.pdf'
    SimpleDocTemplate(str(feature),pagesize=(210*mm,297*mm),leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=20*mm,title='Reversium Feature List',author='3Sci Labs').build(story,onFirstPage=footer,onLaterPages=footer)
    journey_pdf=out/'Reversium-User-Journeys.pdf'
    c=canvas.Canvas(str(journey_pdf),pagesize=(210*mm,297*mm));c.setTitle('Reversium: Seven User Journeys');c.setAuthor('3Sci Labs')
    def para(text,x,y,width,style):
        p=Paragraph(esc(text),style);_,h=p.wrap(width,1000);p.drawOn(c,x,y-h);return y-h
    for i,j in enumerate(data['journeys'],1):
        c.setFillColor(colors.HexColor('#17253c'))
        y=para('Reversium by 3Sci Labs',18*mm,279*mm,174*mm,styles['Title'])
        y=para(str(i)+' / 7 - '+j['title'],18*mm,y-8,174*mm,styles['Heading1'])
        y=para(j['who']+' - '+j['goal'],18*mm,y-8,174*mm,styles['BodyText'])
        top=min(y-15,650)
        for n,(label,detail) in enumerate(j['steps'],1):
            yy=top-(n-1)*94
            c.setFillColor(colors.HexColor('#edf1ff'));c.setStrokeColor(colors.HexColor('#c4cfe6'));c.roundRect(18*mm,yy-76,174*mm,76,10,fill=1,stroke=1)
            para(str(n)+'. '+label,24*mm,yy-10,162*mm,styles['Heading2'])
            para(detail,24*mm,yy-36,162*mm,styles['BodyText'])
            if n<4:
                c.setStrokeColor(colors.HexColor('#4058da'));c.setLineWidth(2);c.line(105*mm,yy-79,105*mm,yy-89);c.line(105*mm-4,yy-85,105*mm,yy-89);c.line(105*mm+4,yy-85,105*mm,yy-89)
        yy=top-4*94-4
        yy=para('Take away: '+j['output'],18*mm,yy,174*mm,styles['BodyText'])
        para('Boundary: '+j['limit'],18*mm,yy-8,174*mm,styles['BodyText'])
        c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#465570'));c.drawString(18*mm,12*mm,'3Sci Labs / '+data['reviewed_on']+' / Build '+__version__);c.drawRightString(192*mm,12*mm,str(i));c.showPage()
        (diagrams/(j['id']+'.svg')).write_text(journey_svg(j),encoding='utf-8')
    c.save()
    section=journeys_section(data)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Seven Reversium user journeys</title><style>body{font:17px system-ui;color:#17253c;background:#f5f7ff}main{max-width:900px;margin:30px auto;padding:24px}a{color:#354dc8}</style><main><a href="../web/">Open Reversium</a> / <a href="user-guide.html">Help</a><h1>Seven common user journeys</h1><p>Build '+__version__+' / '+data['reviewed_on']+'</p><p><a href="../output/pdf/Reversium-User-Journeys.pdf" download>Download all seven journeys (PDF)</a></p>'+section+'</main></html>'
    (ROOT/'docs/user-journeys.html').write_text(page,encoding='utf-8')
    tracked=[feature,journey_pdf,ROOT/'docs/user-journeys.html']+sorted(diagrams.glob('*.svg'))
    manifest={'version':__version__,'catalog_sha256':asset_hash(CATALOG),'artifacts':{p.relative_to(ROOT).as_posix():asset_hash(p) for p in tracked}}
    (ROOT/'docs/product-docs-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Built feature list, seven journey diagrams and journey PDF for',__version__)
    return data,section


if __name__=='__main__':build()
