#!/usr/bin/env python3
"""Data-admin only: create cutoff-filtered inputs; no return/label computation."""
import argparse
from collections import Counter
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab.schema import filter_records,read_json,sha256,validate_input,write_once

def safe_replay_metadata(meta):
    # Administrative current coverage, future split proofs/counts and provider
    # errors must never cross into a KNOWN_AT_T packet. No arbitrary passthrough.
    keys=('price_basis','return_basis','tradability','original_vintage_status',
          'availability_convention','point_in_time_quality')
    cleaned={k:meta[k] for k in keys if k in meta}
    if cleaned.get('price_basis')=='AS_REPORTED_OHLC_NO_ADJCLOSE':
        cleaned['no_splits_in_analysis_interval_confirmed']=meta.get('no_splits_in_analysis_interval_confirmed',False)
    return cleaned

def import_dataset(bundle_path,selection_path,exante_dir):
    bundle,selection=read_json(bundle_path),read_json(selection_path)
    target=Path(exante_dir)
    manifest={"round_id":"ROUND_002","information_set":"KNOWN_AT_T_ONLY","source_bundle_sha256":sha256(bundle_path),"selection_sha256":sha256(selection_path),"inputs":{}}
    for episode in selection["episodes"]:
        asset=bundle["assets"][episode["asset_id"]]
        cutoff=episode["cutoff_at"]
        prices,price_reject=filter_records(asset["prices"],cutoff,allow_reconstructed_prices=True)
        actions,action_reject=filter_records(asset.get("actions",[]),cutoff,allow_reconstructed_actions=True)
        context,context_reject=filter_records(asset.get("context",[]),cutoff)
        packet={**episode,"currency":asset["currency"],"instrument_type":asset.get("instrument_type","UNKNOWN"),"cost_bps_roundtrip":asset.get("cost_bps_roundtrip",50.),"metadata":safe_replay_metadata(asset.get("metadata",{})),"prices":prices,"actions":actions,"context":context,"filter_audit":{"kept_price_rows":len(prices)}}
        # Future price dates and record IDs do not cross into Stage A.
        validate_input(packet)
        path=target/(episode["episode_id"]+".input.v001.json")
        if path.exists():
            if read_json(path)!=packet: raise ValueError("input differs; append version required")
        else: write_once(path,packet)
        manifest["inputs"][episode["episode_id"]]={"path":path.name,"sha256":sha256(path),"cutoff_at":cutoff}
    mp=target/"manifest.json"
    if mp.exists():
        if read_json(mp)!=manifest: raise ValueError("manifest differs")
    else: write_once(mp,manifest)
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",required=True);p.add_argument("--selection",required=True);p.add_argument("--exante-dir",required=True)
    a=p.parse_args();m=import_dataset(a.bundle,a.selection,a.exante_dir)
    print("Admin import:",len(m["inputs"]),"filtered episode inputs; no outcomes computed")
if __name__=="__main__": main()
