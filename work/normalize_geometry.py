import zipfile,re,os
from lxml import etree
p=r'C:\Users\seree\Documents\Codex\2026-10-09\schedule-aware-fault-diagnosis-for-urban\outputs\schedule_aware_irrigation_fault_diagnosis.docx'; q=p+'.geom'
with zipfile.ZipFile(p) as a, zipfile.ZipFile(q,'w',zipfile.ZIP_DEFLATED) as b:
 for it in a.infolist():
  d=a.read(it.filename)
  if it.filename=='word/document.xml':
   root=etree.fromstring(d); w=etree.QName(root).namespace
   def twips(v): return str(round(float(v[:-2])*20)) if v.endswith('pt') else v
   for el in root.iter():
    ln=etree.QName(el).localname
    if ln=='pgSz':
     for k in ('w','h'):
      if el.get('{%s}%s'%(w,k),'').endswith('pt'): el.set('{%s}%s'%(w,k),twips(el.get('{%s}%s'%(w,k))))
    if ln in ('pgMar','cols'):
     for k in el.attrib:
      if el.get(k).endswith('pt'): el.set(k,twips(el.get(k)))
   d=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
  b.writestr(it,d)
os.replace(q,p)
