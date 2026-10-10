#!/usr/bin/env python3
"""Prepare local-only owner-private download assets; never creates or deploys a Site.

Run with the complete final ZIP files as positional arguments. Writes to a new site
folder; refuses to overwrite. Each static object is capped at 20 MiB so no ZIP must
be weakened or omitted to satisfy hosting's per-asset size limit.
"""
import argparse, hashlib, html, json, pathlib, zipfile

HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Investment Research Lab 文件下载</title>
<style>body{font:16px/1.6 system-ui,sans-serif;color:#182133;background:#f3f5f8;max-width:850px;margin:0 auto;padding:28px}h1{font-size:26px}article{background:white;border:1px solid #ccd4df;padding:22px;margin:20px 0;border-radius:8px}button{font:inherit;color:white;background:#154bbc;border:0;padding:12px 18px;border-radius:6px;cursor:pointer}button:disabled{opacity:.6}code{word-break:break-all;font-size:14px}p{margin:12px 0}.status{min-height:48px}a{color:#154bbc}</style></head>
<body><h1>Investment Research Lab 文件下载</h1><p>点击下载，保存完整 ZIP。文件将保持原始内容，下载时会检查分块完整性。</p><main id="files"></main>
<script>
'use strict';
const files = __FILES__;
const toHex = b => Array.from(new Uint8Array(b), v => v.toString(16).padStart(2, '0')).join('');
async function getPart(part){
  const response = await fetch(part.path, {credentials:'same-origin',cache:'no-store'});
  if(!response.ok) throw new Error(`文件读取失败 (${response.status})，请重试。`);
  const bytes = await response.arrayBuffer();
  if(bytes.byteLength!==part.size || toHex(await crypto.subtle.digest('SHA-256',bytes))!==part.sha256) throw new Error('文件完整性检查失败，请重试。');
  return bytes;
}
for(const file of files){
  const box=document.createElement('article');
  const title=document.createElement('h2'); title.textContent=file.name; box.append(title);
  const desc=document.createElement('p'); desc.textContent=`${(file.size/1024/1024).toFixed(1)} MB · 完整研究包`; box.append(desc);
  const button=document.createElement('button'); button.textContent='下载完整 ZIP'; box.append(button);
  const status=document.createElement('p'); status.className='status'; status.setAttribute('role','status'); status.setAttribute('aria-live','polite'); box.append(status);
  const digest=document.createElement('p'); digest.textContent='SHA-256：'; const code=document.createElement('code');code.textContent=file.sha256;digest.append(code);box.append(digest);
  button.addEventListener('click',async()=>{
    button.disabled=true;
    let writable=null;
    try{
      let completed=0;
      const buffers=[];
      if('showSaveFilePicker' in window){
        const handle=await window.showSaveFilePicker({suggestedName:file.name,types:[{description:'ZIP 研究文件',accept:{'application/zip':['.zip']}}]});
        writable=await handle.createWritable();
      }
      for(const part of file.parts){
        status.textContent=`正在下载并检查文件：${Math.round(completed/file.size*100)}%`;
        const bytes=await getPart(part);
        if(writable) await writable.write(bytes); else buffers.push(bytes);
        completed+=bytes.byteLength;
      }
      if(completed!==file.size) throw new Error('文件长度检查失败。');
      if(writable){await writable.close();writable=null;}
      else{
        const blob=new Blob(buffers,{type:'application/zip'});
        if(toHex(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer()))!==file.sha256) throw new Error('完整 ZIP 校验失败。');
        const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=file.name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
      }
      status.textContent='完整性检查通过。请在浏览器下载记录或你选择的文件夹查看 ZIP。';
    }catch(error){
      if(writable)try{await writable.abort();}catch(e){}
      status.textContent=error.name==='AbortError'?'已取消。可以再次点击下载。':error.message;
    }finally{button.disabled=false;}
  });
  document.getElementById('files').append(box);
}
</script></body></html>'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('zipfiles',nargs='+',type=pathlib.Path)
    p.add_argument('--out',type=pathlib.Path,default=pathlib.Path('/workspace/outputs/delivery_access/site'))
    args=p.parse_args()
    if args.out.exists(): raise SystemExit('Refusing to overwrite existing site folder: '+str(args.out))
    for source in args.zipfiles:
        if not source.is_file(): raise SystemExit('Missing ZIP: '+str(source))
        with zipfile.ZipFile(source) as archive:
            corrupt=archive.testzip()
            if corrupt: raise SystemExit('Corrupt ZIP member: '+corrupt)
    dist=args.out/'dist';dist.mkdir(parents=True)
    files=[]
    for number,source in enumerate(args.zipfiles,1):
        parts=[];total=0;whole=hashlib.sha256()
        folder=dist/f'package-{number}';folder.mkdir()
        with source.open('rb') as f:
            while chunk:=f.read(20*1024*1024):
                path=folder/f'{len(parts)+1:03d}.bin';path.write_bytes(chunk)
                parts.append({'path':path.relative_to(dist).as_posix(),'size':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
                total+=len(chunk);whole.update(chunk)
        files.append({'name':source.name,'size':total,'sha256':whole.hexdigest(),'parts':parts})
    encoded=json.dumps(files,ensure_ascii=False).replace('<','\\u003c')
    (dist/'index.html').write_text(HTML.replace('__FILES__',encoded),encoding='utf-8')
    (dist/'manifest.json').write_text(json.dumps({'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    hidden=args.out/'.openai';hidden.mkdir()
    (hidden/'hosting.json').write_text(json.dumps({'static':{'directory':'dist'}},indent=2)+'\n')
    (dist/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  Cache-Control: private, no-store\n',encoding='utf-8')
    print(json.dumps({'local_only':True,'site_folder':str(args.out),'files':[{k:v for k,v in x.items() if k!='parts'} for x in files],'max_asset_bytes':20*1024*1024},ensure_ascii=False))
if __name__=='__main__':main()
