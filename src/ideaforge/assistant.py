from __future__ import annotations
import json, os, re
from dataclasses import dataclass, asdict
from typing import List

ARCHITECTURES=[
("Descriptive","What patterns, subgroups, or anomalies characterize {topic} in {domain}?"),
("Predictive","Can routinely available data predict important outcomes related to {topic} early enough to support action in {domain}?"),
("Integrative","Can heterogeneous data sources be combined to explain and predict {topic} more effectively than isolated measures in {domain}?"),
("Causal","Which modifiable mechanisms causally influence {topic}, and under what conditions do those effects change in {domain}?"),
("Intervention","Can a targeted intervention measurably improve outcomes associated with {topic} compared with current practice in {domain}?"),
("Cross-domain","Can methods from a complementary discipline reveal a useful representation or intervention for {topic} in {domain}?"),
("Resource-constrained","Can {topic} be addressed accurately and safely using low-cost data, limited infrastructure, or scarce expertise in {domain}?"),
("High-risk/high-reward","Can a radically different representation of {topic} expose a mechanism or capability that current approaches systematically miss in {domain}?"),
("Translational","Can evidence about {topic} be converted into a deployable decision-support workflow with measurable real-world benefit in {domain}?"),
("Commercialization-oriented","Can an auditable digital product addressing {topic} create measurable value for a clearly identifiable user and paying organization in {domain}?"),
]

def generate_questions(keyword,domain="General",n=5,goal="Balanced",novelty="Moderate"):
    topic=keyword.strip() or "the selected problem"; dom=domain.strip() or "the selected domain"
    arr=[]
    order=ARCHITECTURES[:]
    if goal.lower().startswith("startup"): order=order[-3:]+order[1:-3]+order[:1]
    if novelty.lower()=="high": order=order[6:]+order[:6]
    for i,(kind,tpl) in enumerate(order[:max(1,min(int(n),10))],1):
        arr.append({"id":f"G{i}","architecture":kind,"question":tpl.format(topic=topic,domain=dom)})
    return arr

def _term_score(text,terms,base=1):
    t=text.lower(); return min(4,base+sum(1 for x in terms if x in t))

def guided_estimate(question,domain="General",background="",resources="",market_context=""):
    """Transparent preliminary estimator. Not a measurement of theoretical DPT constructs."""
    text=" ".join([question,domain,background,resources,market_context]).lower()
    time=_term_score(text,["longitudinal","prospective","multi-year","clinical trial"],1)
    conceptual=_term_score(text,["causal","multimodal","cross-domain","novel","autonomous","mechanism"],1)
    search=_term_score(text,["systematic","historical","multi-domain","literature","evidence synthesis"],1)
    experiment=_term_score(text,["prospective","pilot","field","trial","intervention","deployment"],1)
    compute=_term_score(text,["ai","machine learning","multimodal","large-scale","simulation","digital twin"],1)
    coordination=_term_score(text,["hospital","university","multi-site","stakeholder","regulatory","community"],1)
    # representation proxy: deliberately coarse and editable
    concepts=max(8,min(40,len(set(re.findall(r"[a-zA-Z]{5,}",question.lower())))))
    l_before=max(20,round(concepts*2.2))
    integration_hits=sum(k in text for k in ["combine","integrate","joint","unify","multimodal","predict","automatically","causal"])
    reduction=min(.75,.22+.07*integration_hits)
    l_after=max(4,round(l_before*(1-reduction)))
    market=_term_score(text,["cost","risk","waste","dropout","disease","fraud","delay","energy","safety"],1)
    buyer=_term_score(text,["university","hospital","clinic","company","government","school","farm","enterprise"],1)
    deploy=_term_score(text,["ai","digital","platform","software","app","dashboard","decision-support"],1)
    scale=_term_score(text,["multi-site","platform","university","hospital","community","smallholder","enterprise"],1)
    social=_term_score(text,["health","education","rural","safety","energy","environment","public","student"],1)
    vals=[time,conceptual,search,experiment,compute,coordination]
    conf="Moderate" if between(sum(vals)/6,1.3,2.8) else "Low"
    rationale=("Preliminary transparent suggestion derived from keywords and problem structure only. "
               "Review every value against the declared Reality Space, background knowledge, admissible procedures and representation language.")
    return {"time":time,"conceptual":conceptual,"search":search,"experiment":experiment,"compute":compute,"coordination":coordination,
            "l_before":float(l_before),"l_after":float(l_after),"market_pain":market,"buyer_clarity":buyer,
            "digital_deployability":deploy,"scale_potential":scale,"social_impact":social,"confidence":conf,"rationale":rationale}

def between(x,a,b): return a<=x<=b

def openai_estimate(question,domain="General",background="",resources="",market_context="",model=None):
    key=os.getenv("OPENAI_API_KEY")
    if not key: return None
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key); model=model or os.getenv("OPENAI_MODEL","gpt-5-mini")
        schema="""Return JSON only with integer 0-4 keys time, conceptual, search, experiment, compute, coordination, market_pain, buyer_clarity, digital_deployability, scale_potential, social_impact; numeric l_before>0; numeric l_after>=0; confidence Low/Moderate/High; rationale under 120 words. Scores are preliminary suggestions, not measurements."""
        prompt=f"{schema}\nQuestion: {question}\nDomain: {domain}\nBackground: {background}\nResources: {resources}\nMarket context: {market_context}"
        rsp=client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            response_format={"type":"json_object"},
        )
        txt=(rsp.choices[0].message.content or "").strip()
        txt=re.sub(r"^```json|```$","",txt,flags=re.M).strip()
        return json.loads(txt)
    except Exception:
        return None
