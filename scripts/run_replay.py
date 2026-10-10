#!/usr/bin/env python3
"""Run Stage A in a process-level read guard, or separately Stage B after all locks."""
import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab.schema import utc_now

def install_stage_a_guard(exante_dir,output_dir,selection,preregistration):
    read_dirs=[Path(exante_dir).resolve()]
    write_dir=Path(output_dir).resolve()
    read_output_dirs=[write_dir/"predictions",write_dir/"locks"]
    read_output_files={write_dir/"all_locks.v001.json"}
    exact_files={Path(selection).resolve(),Path(preregistration).resolve()}
    code_root=Path(__file__).resolve().parents[1]
    exact_files.update(code_root/name for name in ("lab/schema.py","lab/replay.py","lab/evaluate.py","lab/select.py","scripts/run_replay.py"))
    def beneath(path,parent): return path==parent or parent in path.parents
    def hook(event,args):
        if event!="open": return
        value,mode,flags=args
        if isinstance(value,int): return  # existing stdio descriptors
        path=Path(os.fsdecode(value)).resolve()
        writing=(isinstance(mode,str) and any(c in mode for c in "wax+")) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if writing:
            if not beneath(path,write_dir): raise PermissionError("Stage A write outside output rejected: "+str(path))
        elif path not in exact_files and not any(beneath(path,d) for d in read_dirs+read_output_dirs) and path not in read_output_files:
            raise PermissionError("Stage A forbidden read rejected: "+str(path))
    sys.addaudithook(hook)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=["A","B"])
    p.add_argument("--exante-dir",required=True);p.add_argument("--output-dir",required=True)
    p.add_argument("--selection",required=True);p.add_argument("--preregistration",required=True)
    p.add_argument("--labels",help="Stage B only; never opened by Stage A")
    a=p.parse_args()
    if a.stage=="A":
        if a.labels: raise ValueError("Stage A cannot accept label path")
        from lab.replay import run_stage_a
        # All modules loaded before guard; guard protects application-level reads.
        install_stage_a_guard(a.exante_dir,a.output_dir,a.selection,a.preregistration)
        result=run_stage_a(a.exante_dir,a.output_dir,a.selection,a.preregistration)
        print(utc_now(),result["status"],len(result["episode_ids"]))
    else:
        if not a.labels: raise ValueError("Stage B requires --labels")
        from lab.evaluate import run_stage_b
        result=run_stage_b(a.output_dir,a.exante_dir,a.selection,a.preregistration,a.labels)
        print(utc_now(),result["status"],result["episode_count"])
if __name__=="__main__": main()
