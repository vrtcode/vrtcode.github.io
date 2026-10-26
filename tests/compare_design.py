from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Code-level parity against the reviewed owner-supplied design; no template JavaScript is executed.')
parser.add_argument('design',type=Path)
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
from html.parser import HTMLParser
import re,json,html
s=args.design.read_text();start=s.index('<header style="position:sticky');end=s.index('</header>',start)+9
class P(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'style' in a:self.items.append((tag,a))
p=P();p.feed(s[start:end]);css=(ROOT/'src/enhancements.css').read_text()
def declarations(s):return dict(x.split(':',1) for x in s.split(';') if x)
def rules(selector):
 m=re.search(re.escape(selector)+r'\{([^{}]*)\}',css)
 if not m:raise ValueError(selector)
 return declarations(m[1])
maps=[['.site-header'],['.header-inner'],['.wordmark'],['.wordmark span'],['.desktop-nav'],['.desktop-nav ul'],['.desktop-nav ul a'],['.header-github'],['.header-github>span:first-child'],['.sr-only'],['.menu-button'],['.mobile-nav'],['.mobile-nav ul'],['.mobile-nav li:not(:last-child)'],['.mobile-nav a'],['.nav-num'],['.mobile-nav a','.mobile-nav .mobile-github']]
report=[]
for (tag,a),selectors in zip(p.items,maps):
 expected=declarations(a['style']);actual={}
 for selector in selectors:actual.update(rules(selector))
 differences={k:{'source':v,'target':actual.get(k)} for k,v in expected.items() if actual.get(k)!=v}
 # Both forms are equivalent CSS rect syntax; the sr-only utility adds robust hidden-text resets.
 if selectors==['.sr-only'] and differences=={'clip':{'source':'rect(0 0 0 0)','target':'rect(0,0,0,0)'}}:differences={}
 # Mobile GitHub has a flex-start value inherited from the common link rule; this has no visual effect for one text node.
 hover={}
 if 'style-hover' in a:
  actual_hover=rules(selectors[0]+':hover');hover={k:{'source':v,'target':actual_hover.get(k)} for k,v in declarations(a['style-hover']).items() if actual_hover.get(k)!=v}
 report.append({'tag':tag,'selectors':selectors,'declarations_checked':len(expected),'differences':differences,'hover_differences':hover})

assert len(report)==17
assert not any(r['differences'] or r['hover_differences'] for r in report)

# The original template is retained, except for these explicit migration edits.
body=s.split('</helmet>')[1].split('</x-dc>')[0]
a=body.index('<header style="position:sticky;');b=body.index('</header>',a)+len('</header>')
body=body[:a]+'{{ siteHeader }}'+body[b:]
body=body.replace('ref="{{ netRef }}"','id="network-bg"')
changes=[
 ('These groups describe tools used in the discussed projects, not a personal proficiency scale.','Tools used across research and engineering projects.'),
 ('case {{ cs.num }} of 07','case {{ cs.num }} of {{ caseCount }}'),
 ('What was established, and what stayed open.','Implementation notes, engineering principles, and open questions.')]
for old,new in changes:
 assert body.count(old)==1, 'Expected original template text was not found'
 body=body.replace(old,new)
# Apply the operator-requested copy revision without allowing markup/style changes.
journal=json.loads((ROOT/'verification/copy-rewrite.json').read_text())
copy={e['old']:e['new'] for e in journal['templateText'] if e['file']=='src/body.html'}
def rewrite_text(match):
 raw=match[0];clean=html.unescape(raw.strip())
 if clean not in copy:return raw
 return raw[:len(raw)-len(raw.lstrip())]+html.escape(copy[clean],quote=False)+raw[len(raw.rstrip()):]
body=re.sub(r'(?<=>)[^<>]+(?=<)',rewrite_text,body)
assert body.strip()+'\n'==(ROOT/'src/body.html').read_text(), 'Unlisted body-template or markup/style difference'
assert re.search(r'<style>([\s\S]*?)</style>',s)[1].strip()+'\n'==(ROOT/'src/base.css').read_text(), 'Original global CSS changed'
print(json.dumps({'globalCss':'EXACT','bodyTemplate':'EXACT markup/styles after explicit migration and conversational-copy changes',
 'headerElements':len(report),'headerDeclarations':sum(r['declarations_checked'] for r in report),
 'headerHover':'MATCH','originalShadowDeclarations':len(re.findall(r'(?:box|text)-shadow\s*:',s))},indent=2))
