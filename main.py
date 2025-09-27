import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Create paths and dataframes
target_path = "data/interactions.csv"
twosides_path = "data/TWOSIDES_filtered.csv"
target_df = pd.read_csv(target_path, skiprows=1)
twosides_df = pd.read_csv(twosides_path)

# Initialize API and allow requests
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RESPONSE MODELS
class TargetResponse(BaseModel):
    interaction: bool
    targets: Optional[list[str]] = Field(default=None, description="Shared receptor target(s) of drugs")

class DDIResponse(BaseModel):
    interaction: bool
    conditions_and_prr: Optional[dict[str, float]] = Field(default=None, description="Condition : PRR dictionary")

class CombinedResponse(BaseModel):
    interaction: bool
    targets: Optional[list[str]] = Field(default=None, description="Shared receptor target(s) of drugs")
    conditions_and_prr: Optional[dict[str, float]] = Field(default=None, description="Condition : PRR dictionary")

# PREPROCESSING
# Target Preprocessing
target_df['Ligand'] = target_df['Ligand'].str.strip().str.lower()

targets_dict = {}
for target, group in target_df.groupby("Target"):
    ligands = set(group['Ligand'])
    for d1 in ligands:
        for d2 in ligands:
            if d1 < d2:
                pair = frozenset([d1, d2])
                if pair not in targets_dict:
                    targets_dict[pair] = []
                targets_dict[pair].append(target)

# TWOSIDES Preprocessing
twosides_df["drug_1_concept_name"] = twosides_df["drug_1_concept_name"].str.strip().str.lower()
twosides_df["drug_2_concept_name"] = twosides_df["drug_2_concept_name"].str.strip().str.lower()

twosides_df["pair"] = twosides_df.apply(lambda x: frozenset([x["drug_1_concept_name"], x["drug_2_concept_name"]]), axis=1)
twosides_dict = (twosides_df.groupby("pair")[["condition_concept_name", "PRR"]].apply(lambda x: dict(zip(x["condition_concept_name"], x["PRR"]))).to_dict())

# ENDPOINTS
# Return shared receptor target(s) if drugs bind to the same target
@app.get('/targets/', response_model=TargetResponse)
def check_target(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
                 drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    pair = frozenset([drug1.strip().lower(), drug2.strip().lower()])
    target = targets_dict.get(pair)

    if target:
        return TargetResponse(interaction=True, targets=target)

    return TargetResponse(interaction=False)

# Return conditions and PRR if drugs have a DDI
@app.get('/interactions/', response_model=DDIResponse)
def check_ddi(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
              drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    pair = frozenset([drug1.strip().lower(), drug2.strip().lower()])
    conditions_and_prr = twosides_dict.get(pair)

    if conditions_and_prr:
        sorted_conditions_and_prr = dict(sorted(conditions_and_prr.items(), key=lambda items: items[1], reverse=True))
        return DDIResponse(interaction=True, conditions_and_prr=sorted_conditions_and_prr)

    return DDIResponse(interaction=False)

# Return receptor targets(s), conditions and PRR if they exist and drugs have a DDI
@app.get('/full_interactions/', response_model=CombinedResponse)
def check_combined(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
                   drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    pair = frozenset([drug1.strip().lower(), drug2.strip().lower()])
    target = targets_dict.get(pair)
    conditions_and_prr = twosides_dict.get(pair)

    sorted_conditions_and_prr = None
    if conditions_and_prr:
        sorted_conditions_and_prr = dict(sorted(conditions_and_prr.items(), key=lambda items: items[1], reverse=True))
    if target or sorted_conditions_and_prr:
        return CombinedResponse(interaction=True, targets=target, conditions_and_prr=sorted_conditions_and_prr)
    
    return CombinedResponse(interaction=False)
