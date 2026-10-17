"""Report subsection navigation shared by browser and local editions."""
import re
from .branding import HEADER


def subsections(content, prefix, markers):
    parts=[]
    for marker,label in markers:
        pos=content.find(marker)
        if pos>=0: parts.append((pos,label))
    parts.sort()
    if not parts:return content
    navigation='<nav class="subnav" aria-label="'+prefix+' sections">'
    sections=''
    for i,(pos,label) in enumerate(parts):
        identity=prefix+'-'+str(i)
        navigation+='<button data-subsection="'+identity+'" aria-pressed="'+('true' if i==0 else 'false')+'">'+label+'</button>'
        end=parts[i+1][0] if i+1<len(parts) else len(content)
        sections+='<section class="subsection" id="'+identity+'">'+content[pos:end]+'</section>'
    return navigation+'</nav>'+sections


def layout(page):
    page=re.sub(r'<p class="brand">REVERSIUM .*? / LOCAL ANALYSIS</p>',HEADER,page,count=1)
    page=page.replace('<h1>Your file review is complete.</h1>','')
    page=page.replace('<details><summary>Technical inventory numbers</summary>','<section class="inventory-numbers"><h2>Technical inventory numbers</h2>')
    page=page.replace('Counts show inspected material, not how complete or reliable the software is.</p></details>','Counts show inspected material, not how complete or reliable the software is.</p></section>')
    groups={
      'architecture': [('<h2>Follow one workflow','Workflow'),('<details id="full-feature-map"','Graphical feature map'),('<h2>Feature catalogue','Feature catalogue'),('<h2>Platform profile','Platform profile'),('<h2>Supporting services','Supporting services'),('<h2 id="file-relationships"','Imports & dependencies')],
      'coverage':[('<h2>What this report can explain','Overview'),('<h2>Binary inspection','Binary inspection'),('<h2>Inventory','File inventory'),('<h2>Setup and readiness','Setup & readiness'),('<h2>Coverage and limitations','Limitations')]
    }
    for group,markers in groups.items():
        pattern=r'(<section role="tabpanel" id="panel-'+group+r'"[^>]*>)(.*?)(</section>\s*<section role="tabpanel")'
        def replace(match):
            content=match[2]
            if group=='architecture':content=content[content.index('<h2>Follow one workflow'):]
            return match[1]+subsections(content,group,markers)+match[3]
        page=re.sub(pattern,replace,page,count=1,flags=re.S)
    return page
