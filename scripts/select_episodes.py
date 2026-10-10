#!/usr/bin/env python3
"""Freeze metadata-only calendar selection. Never reads market observations."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab.schema import read_json,write_once
from lab.select import select_episodes

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--universe",required=True,help="JSON array of asset metadata")
    p.add_argument("--output",required=True)
    p.add_argument("--cutoffs",nargs="+",default=[f"{year}-09-30" for year in range(2016,2024)])
    a=p.parse_args()
    obj=select_episodes(read_json(a.universe),a.cutoffs)
    if Path(a.output).exists():
        if read_json(a.output)!=obj: raise ValueError("selection already exists with different content")
    else: write_once(a.output,obj)
    print("Selection frozen:",len(obj["episodes"]),"episodes; no returns inspected")
if __name__=="__main__": main()
