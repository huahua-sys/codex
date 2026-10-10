"""Synthetic engineering tests only: not evidence for an investment principle."""
import copy
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lab.schema import filter_records,historical_wealth,read_json,sha256,split_ratio,validate_input,write_once
from lab.replay import make_prediction,run_stage_a
from lab.evaluate import evaluate_path,run_stage_b,score_prediction,summarize
from lab.select import select_episodes

def synthetic_prices(n=850):
    out=[];d=date(2018,1,1);i=0
    while len(out)<n:
        if d.weekday()<5:
            price=100*math.exp(.0003*i+.02*math.sin(i/7))
            out.append({"record_id":f"SYNTH-P-{i}","date":d.isoformat(),"session_open_at":d.isoformat()+"T14:30:00+00:00","session_close_at":d.isoformat()+"T21:00:00+00:00","available_at":d.isoformat()+"T22:00:00+00:00","open":price,"high":price*1.01,"low":price*.99,"close":price,"source_id":"SYNTHETIC_ENGINEERING_ONLY","source_sha256":"0"*64,"pit_status":"VERIFIED"})
            i+=1
        d+=timedelta(days=1)
    return out

def packet():
    rows=synthetic_prices(300)
    return {"episode_id":"SYNTH-001","asset_id":"SYNTH","market":"SYNTH","currency":"USD","cutoff_at":rows[-1]["date"]+"T23:59:59+00:00","prices":rows,"actions":[],"context":[],"metadata":{"price_basis":"UNADJUSTED","return_basis":"PRICE_ONLY","tradability":"NONTRADABLE_INDEX"}}

def action(date_,kind,**values):
    return {"record_id":"SYNTH-A-"+kind,"date":date_,"available_at":date_+"T22:00:00+00:00","action_type":kind,"source_id":"SYNTHETIC_ENGINEERING_ONLY","source_sha256":"0"*64,"pit_status":"VERIFIED",**values}

class ReplayEngineering(unittest.TestCase):
    def test_future_record_rejected_even_if_observed_period_earlier(self):
        p=packet();future=copy.deepcopy(p["prices"][-1]);future.update(record_id="FUTURE",date="2020-12-31",available_at="2021-01-01T00:00:00+00:00")
        p["prices"].append(future)
        with self.assertRaisesRegex(ValueError,"POST_CUTOFF"):make_prediction(p)

    def test_price_cutoff_filter_and_uncertain_quarantine(self):
        p=packet();past=p["prices"][:-1];future=copy.deepcopy(p["prices"][-1]);future["available_at"]="2030-01-01T00:00:00+00:00"
        unknown=copy.deepcopy(p["prices"][-1]);unknown.update(record_id="UNKNOWN",pit_status="POINT_IN_TIME_UNCERTAIN")
        kept,rejected=filter_records(past+[future,unknown],p["cutoff_at"])
        self.assertEqual(kept,past);self.assertEqual({x["reason"] for x in rejected},{"KNOWN_ONLY_AFTER_T","POINT_IN_TIME_UNCERTAIN"})

    def test_intraday_close_leak_missing_open_and_nonfinite_split(self):
        p=packet();last=p["prices"][-1]
        last["available_at"]=last["date"]+"T14:31:00+00:00"
        p["cutoff_at"]=last["date"]+"T15:00:00+00:00"
        with self.assertRaisesRegex(ValueError,"before session close"):make_prediction(p)
        rows=synthetic_prices(8);del rows[0]["session_open_at"]
        with self.assertRaisesRegex(ValueError,"explicit session_open_at"):evaluate_path(rows,[],"2017-12-31T23:59:59+00:00",5)
        for ratio in (float('nan'),float('inf'),0,-1):
            with self.assertRaises(ValueError):split_ratio({"ratio":ratio})

    def test_nonprice_publication_cannot_be_backdated(self):
        p=packet();row={"record_id":"SYNTH-M","source_id":"SYNTHETIC_ENGINEERING_ONLY","source_sha256":"0"*64,"category":"Macro","value":2.,"pit_status":"VERIFIED","published_at":"2030-01-01T00:00:00+00:00","available_at":"2018-01-01T00:00:00+00:00","availability_evidence":"synthetic proof"}
        p["context"]=[row]
        with self.assertRaisesRegex(ValueError,"publication after"):make_prediction(p)
        row.update(published_at="2018-01-01T00:00:00+00:00",pit_status="POINT_IN_TIME_UNCERTAIN")
        with self.assertRaisesRegex(ValueError,"ineligible PIT"):make_prediction(p)

    def test_total_return_split_and_dividend_entry_and_exit(self):
        rows=synthetic_prices(4)
        for row,price in zip(rows,[100,50,49,49]):row.update(open=price,high=price,low=price,close=price)
        # Entry first session excludes same-day dividend; second splits 2:1;
        # third $1 per post-split share offsets its 1$ price drop.
        acts=[action(rows[0]["date"],"dividend",amount=7.),action(rows[1]["date"],"split",ratio=2.),{**action(rows[2]["date"],"dividend",amount=1.),"record_id":"DIV2"}]
        r=evaluate_path(rows,acts,"2017-12-31T23:59:59+00:00",3,"COMPLETE","TOTAL_RETURN",0.)
        self.assertAlmostEqual(r["gross_return"],0.)
        self.assertAlmostEqual(historical_wealth(rows,acts)[-1][1],1.)
        # Order of same-date dividend/split inputs cannot change wealth.
        same=[action(rows[1]["date"],"dividend",amount=1.),action(rows[1]["date"],"split",ratio=2.)]
        self.assertEqual(historical_wealth(rows,same),historical_wealth(rows,list(reversed(same))))

    def test_missing_outcome_not_zero_and_unknown_actions_not_total_return(self):
        rows=synthetic_prices(4)
        r=evaluate_path(rows,[],"2017-12-31T23:59:59+00:00",5)
        self.assertEqual(r["status"],"PENDING_HORIZON");self.assertIsNone(r["gross_return"])
        r=evaluate_path(rows,[],"2017-12-31T23:59:59+00:00",2,"UNKNOWN","TOTAL_RETURN")
        self.assertEqual(r["status"],"UNRESOLVED_DATA");self.assertIsNone(r["max_adverse_excursion"])

    def test_outcome_duplicate_actions_and_foreign_asset_rejected(self):
        p=make_prediction(packet());rows=synthetic_prices()
        first=action(rows[310]["date"],"dividend",amount=1.)
        duplicate={**first,"record_id":"SYNTH-DUPLICATE"}
        with self.assertRaisesRegex(ValueError,"duplicate action economic event"):
            score_prediction(p,{"prices":rows,"actions":[first,duplicate]})
        rows[0]["asset_id"]="FOREIGN"
        with self.assertRaisesRegex(ValueError,"different asset_id"):
            score_prediction(p,{"prices":rows,"actions":[]})

    def test_execution_uses_next_open_and_excludes_exit_session_future_extrema(self):
        rows=synthetic_prices(6);rows[-1]["high"]=100000
        cutoff=rows[0]["date"]+"T23:59:59+00:00"
        r=evaluate_path(rows,[],cutoff,4,"UNKNOWN","PRICE_ONLY",0.)
        self.assertEqual(r["entry_date"],rows[1]["date"])
        self.assertEqual(r["exit_date"],rows[5]["date"])
        self.assertLess(r["max_favorable_excursion"],1.)

    def fixture_round(self,d):
        ex=d/"ex_ante";out=d/"replay";p=packet()
        selection=select_episodes([{"asset_id":"SYNTH","market":"SYNTH","inception_date":"2000-01-01"}],[p["cutoff_at"][:10]])
        p["episode_id"]=selection["episodes"][0]["episode_id"]
        sp=d/"selection.json";pr=d/"prereg.md";ip=ex/(p["episode_id"]+".json")
        write_once(sp,selection);write_once(pr,"SYNTHETIC ENGINEERING ONLY\n",text=True);write_once(ip,p)
        write_once(ex/"manifest.json",{"inputs":{p["episode_id"]:{"path":ip.name,"sha256":sha256(ip)}}})
        lp=d/"future_bundle.json";write_once(lp,{"assets":{"SYNTH":{"prices":synthetic_prices(),"actions":[],"action_coverage":"UNKNOWN","metadata":{"price_basis":"UNADJUSTED","return_basis":"PRICE_ONLY"}}}})
        return ex,out,sp,pr,lp,p

    def test_future_adjusted_outcome_rejected_and_pending_not_revealed(self):
        p=make_prediction(packet())
        bundle={"prices":synthetic_prices(),"actions":[],"action_coverage":"COMPLETE","metadata":{"price_basis":"FUTURE_SPLIT_ADJUSTED"}}
        with self.assertRaisesRegex(ValueError,"future adjusted"):score_prediction(p,bundle)
        bundle={"prices":packet()["prices"],"actions":[],"metadata":{"price_basis":"UNADJUSTED"}}
        ev=score_prediction(p,bundle)
        self.assertEqual(ev["status"],"PENDING_HORIZON")
        self.assertTrue(all(r["net_return"] is None for r in ev["horizons"].values()))

    def test_all_locks_required_before_future_read(self):
        with tempfile.TemporaryDirectory(prefix="round002-synthetic-") as td:
            ex,out,sp,pr,lp,p=self.fixture_round(Path(td))
            with self.assertRaises(FileNotFoundError):run_stage_b(out,ex,sp,pr,lp)
            run_stage_a(ex,out,sp,pr)
            prediction=read_json(out/"predictions"/(p["episode_id"]+".v001.json"))
            self.assertNotIn("prediction_sha256",prediction)
            summary=run_stage_b(out,ex,sp,pr,lp)
            self.assertEqual(summary["episode_count"],1)
            self.assertEqual(summary["horizons"]["12m"]["n_mature"],1)

    def test_write_once_repeat_verifies_and_tampering_blocks_labels(self):
        with tempfile.TemporaryDirectory(prefix="round002-synthetic-") as td:
            ex,out,sp,pr,lp,p=self.fixture_round(Path(td))
            sentinel=run_stage_a(ex,out,sp,pr)
            self.assertEqual(run_stage_a(ex,out,sp,pr),sentinel)
            pp=out/"predictions"/(p["episode_id"]+".v001.json")
            with self.assertRaises(FileExistsError):write_once(pp,{})
            pp.write_text(pp.read_text()+" ")
            with self.assertRaisesRegex(ValueError,"integrity"):run_stage_b(out,ex,sp,pr,lp)

    def test_calendar_selection_has_no_outcome_interface(self):
        universe=[{"asset_id":x,"market":x,"inception_date":"1990-01-01"} for x in ["US","HK","JP"]]
        s=select_episodes(universe,[f"{y}-09-30" for y in range(2016,2024)])
        self.assertEqual(len(s["episodes"]),24);self.assertFalse(s["selection_inspects_outcomes"])
        self.assertEqual(len({e["cutoff_at"] for e in s["episodes"]}),8)

    def test_stage_a_subprocess_guard_and_brier_baselines(self):
        with tempfile.TemporaryDirectory(prefix="round002-synthetic-") as td:
            ex,out,sp,pr,lp,p=self.fixture_round(Path(td))
            command=[sys.executable,str(ROOT/"scripts/run_replay.py"),"A","--exante-dir",str(ex),"--output-dir",str(out),"--selection",str(sp),"--preregistration",str(pr)]
            completed=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(completed.returncode,0,completed.stderr)
            summary=run_stage_b(out,ex,sp,pr,lp)
            self.assertAlmostEqual(summary["horizons"]["12m"]["constant_05_brier"],.25)
            guard_source="from scripts.run_replay import install_stage_a_guard\ninstall_stage_a_guard("+repr(str(ex))+","+repr(str(out))+","+repr(str(sp))+","+repr(str(pr))+")\nopen("+repr(str(lp))+").read()"
            blocked=subprocess.run([sys.executable,"-c",guard_source],cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(blocked.returncode,0);self.assertIn("forbidden read",blocked.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
