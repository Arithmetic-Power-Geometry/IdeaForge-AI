import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from ideaforge import *

def rec(qid,q,time,conceptual,search,experiment,compute,coordination,lb,la,**kw):
    return QuestionRecord(qid,q,time,conceptual,search,experiment,compute,coordination,lb,la,**kw)

def energy_records():
    return [
      rec('q1','LED lighting',1,1,1,1,0,1,40,35,market_pain=3,buyer_clarity=4,digital_deployability=1,scale_potential=3,social_impact=3),
      rec('q2','Timetable peak demand',2,2,2,2,1,3,40,25,market_pain=3,buyer_clarity=4,digital_deployability=2,scale_potential=3,social_impact=3),
      rec('q3','Integrated campus energy',3,3,3,3,3,3,40,8,market_pain=4,buyer_clarity=4,digital_deployability=4,scale_potential=4,social_impact=4),
      rec('q4','Complete self-sufficiency',4,4,4,4,4,4,40,20,market_pain=3,buyer_clarity=3,digital_deployability=2,scale_potential=2,social_impact=4),
    ]

def test_q1_coordinate():
    r=energy_records()[0]; assert discovery_complexity(r)==5; assert round(normalized_discovery_complexity(r),3)==.208; assert question_compression(r)==5; assert normalized_question_compression(r)==.125

def test_q3_coordinate():
    r=energy_records()[2]; assert discovery_complexity(r)==18; assert normalized_discovery_complexity(r)==.75; assert question_compression(r)==32; assert normalized_question_compression(r)==.8

def test_q4_coordinate():
    r=energy_records()[3]; assert discovery_complexity(r)==24; assert normalized_discovery_complexity(r)==1; assert question_compression(r)==20; assert normalized_question_compression(r)==.5

def test_regions():
    df=analyse_records(energy_records()); assert df.region.tolist()==['I','I','IV','III']

def test_frontier_original():
    df=analyse_records(energy_records()); assert df.frontier.tolist()==[True,True,True,False]

def test_utility():
    df=analyse_records(energy_records()); assert round(df.loc[df.question_id=='q3','utility'].iloc[0],3)==.425

def test_q3_venture():
    df=analyse_records(energy_records()); assert round(df.loc[df.question_id=='q3','venture_readiness'].iloc[0],1)==79.0

def test_expansion():
    r=rec('x','expands',1,1,1,1,1,1,20,30); assert signed_change(r)==-10; assert question_compression(r) is None; assert normalized_question_compression(r) is None; assert not compression_explanatory(r); df=analyse_records([r]); assert not bool(df.discovery_plane_eligible.iloc[0]); assert df.region.iloc[0]=='Excluded'; assert not bool(df.frontier.iloc[0])

def test_equivalence_classes():
    rs=energy_records()+[rec('x','same coordinate',2,2,2,2,2,2,40,20)]
    df=analyse_records(rs); x=df[df.question_id=='x'].iloc[0]
    assert x.dc==.5 and x.qc==.5 and df.coordinate_class.nunique()==5

def test_dynamic_frontier_change():
    rs=energy_records()+[rec('x','same dc higher qc than q2',2,2,2,2,2,2,40,20)]
    df=analyse_records(rs); assert not bool(df[df.question_id=='q2'].frontier.iloc[0])

def test_generator_diversity():
    qs=generate_questions('student dropout','Education',5); assert len(qs)==5; assert len(set(q['architecture'] for q in qs))==5

def test_guided_estimator_bounds():
    d=guided_estimate('Can AI combine attendance and LMS data to predict student dropout?','Education');
    for k in DC_COMPONENTS: assert 0<=d[k]<=4
    assert d['l_before']>0 and d['l_after']>=0

def test_sensitivity_grid():
    sg=sensitivity_grid(energy_records()); assert len(sg)==7*7*4; assert set(['tau_d','tau_q','lambda','top_question']).issubset(sg.columns)

def test_distance_symmetry():
    a=(.2,.4); b=(.7,.9); assert weighted_distance(a,b)==weighted_distance(b,a)

def test_readiness_not_probability():
    r=energy_records()[2]; s=venture_readiness(r); assert 0<=s<=100


def test_worked_energy_case_loader():
    from pathlib import Path
    from ideaforge import load_worked_energy_case, QuestionRecord, analyse_records
    root = Path(__file__).resolve().parents[1]
    payloads = load_worked_energy_case(root / 'data' / 'worked_energy_case.csv')
    assert len(payloads) == 4
    assert [p['question_id'] for p in payloads] == ['q1','q2','q3','q4']
    records = [QuestionRecord(**p) for p in payloads]
    df = analyse_records(records)
    q3 = df.loc[df.question_id == 'q3'].iloc[0]
    assert round(float(q3.dc), 3) == 0.750
    assert round(float(q3.qc), 3) == 0.800
    assert q3.region == 'IV'
    assert bool(q3.frontier)


def test_workflow_uploads_artifact():
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / '.github' / 'workflows' / 'reproduce.yml').read_text(encoding='utf-8')
    assert 'actions/upload-artifact@v4' in text
    assert 'IdeaForge-AI-v1.0.0-reproducibility' in text
    assert 'path: IdeaForge-AI-v1.0.0-reproducibility-artifact.zip' in text



def test_wizard_has_mode_radio_and_six_steps():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'MODES = ["AI-assisted automatic", "Manual expert"]' in text
    assert 'st.radio(' in text
    assert 'STEP_LABELS' in text
    for label in ['Setup','Questions','Scoring','Portfolio','Startup Studio','Export evidence']:
        assert label in text


def test_ai_flow_generates_all_before_scoring():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'Number of questions to generate' in text
    assert 'Generate all candidate questions' in text
    assert 'Review the complete question set' in text
    assert 'automatically score selected questions' in text
    assert 'build_auto_rows(' in text
    assert 'Accept all reviewed estimates and analyze portfolio' in text


def test_manual_mode_has_explained_inputs_and_popovers():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'Manual mode is the audit baseline' in text
    assert 'st.popover("❓ Help"' in text
    assert 'Representation help' in text
    assert 'Raw DC (infimum)' in text
    assert 'Normalized DC' in text
    assert 'Normalized QC' in text


def test_energy_loader_is_only_public_loader():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'Load worked energy case' in text
    assert 'Load 6-question development portfolio' not in text
    assert 'q1-q4' in text or 'q1–q4' in text


def test_workflow_builds_nonempty_zip_artifact():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'.github'/'workflows'/'reproduce.yml').read_text(encoding='utf-8')
    assert 'Build reproducibility artifact ZIP' in text
    assert 'IdeaForge-AI-v1.0.0-reproducibility-artifact.zip' in text
    assert 'test -s IdeaForge-AI-v1.0.0-reproducibility-artifact.zip' in text
    assert 'path: IdeaForge-AI-v1.0.0-reproducibility-artifact.zip' in text

def test_energy_loader_synchronizes_mode_radio():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'key="mode_radio"' in text
    assert 'st.session_state.mode_radio = "Manual expert"' in text
    assert 'st.session_state.step = 4' in text



def test_formal_finite_procedure_infimum():
    r = rec(
        'p', 'multiple procedures', 4,4,4,4,4,4, 40,20,
        admissible_procedures=[
            {'name':'P1','time':4,'conceptual':4,'search':4,'experiment':4,'compute':4,'coordination':4},
            {'name':'P2','time':1,'conceptual':2,'search':1,'experiment':2,'compute':1,'coordination':1},
        ]
    )
    assert discovery_complexity(r) == 8
    assert normalized_discovery_complexity(r) == 8/24
    assert selected_procedure(r) == 'P2'
    assert len(procedure_costs(r)) == 2


def test_inaccessible_question_has_infinite_dc_and_is_excluded():
    r = rec('inf','inaccessible',1,1,1,1,1,1,40,20,feasible=False)
    assert discovery_complexity(r) == float('inf')
    assert normalized_discovery_complexity(r) == float('inf')
    df = analyse_records([r])
    assert not bool(df.discovery_plane_eligible.iloc[0])
    assert df.region.iloc[0] == 'Excluded'
    assert not bool(df.frontier.iloc[0])


def test_raw_and_normalized_qc_are_distinct():
    r = energy_records()[2]
    assert signed_change(r) == 32
    assert question_compression(r) == 32
    assert normalized_question_compression(r) == .8
    df = analyse_records([r])
    row = df.iloc[0]
    assert row.qc_raw == 32
    assert row.qc == .8
    assert row.qc_scale_used == 40


def test_analysis_reports_raw_and_normalized_dc():
    r = energy_records()[0]
    df = analyse_records([r])
    row = df.iloc[0]
    assert row.dc_raw == 5
    assert round(row.dc, 3) == .208
    assert row.dc_scale_used == 24
    assert row.selected_procedure == 'P1'


def test_expansion_never_enters_frontier_or_sensitivity_ranking():
    exp = rec('x','expands',0,0,0,0,0,0,20,30,market_pain=4,buyer_clarity=4,digital_deployability=4,scale_potential=4,social_impact=4)
    rs = [exp] + energy_records()
    df = analyse_records(rs)
    row = df[df.question_id=='x'].iloc[0]
    assert not row.discovery_plane_eligible
    assert not row.frontier
    sg = sensitivity_grid(rs)
    assert 'x' not in set(sg.top_question)


def test_reports_json_accepts_list_records():
    import json
    b = portfolio_json([{'question_id':'q1','value':1}])
    assert json.loads(b.decode('utf-8'))[0]['question_id'] == 'q1'


def test_streamlit_export_wiring_is_corrected():
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'portfolio_json(st.session_state.records).encode' not in text
    assert 'pdf_bytes = assessment_pdf(row, readiness)' in text


def test_manual_ui_supports_finite_procedure_infimum_and_expansion_exclusion():
    text=(Path(__file__).resolve().parents[1]/'app'/'streamlit_app.py').read_text(encoding='utf-8')
    assert 'Advanced: add alternative admissible procedures' in text
    assert 'Raw DC (infimum)' in text
    assert 'representational expansion' in text.lower()
    assert 'excluded from the nonnegative Discovery Plane' in text
