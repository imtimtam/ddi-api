import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional

# Create paths and dataframes
target_path = "data/interactions.csv"
twosides_path = "data/TWOSIDES_filtered.csv"
target_df = pd.read_csv(target_path, skiprows=1)
twosides_df = pd.read_csv(twosides_path)

# Initialize API
app = FastAPI()

class TargetResponse(BaseModel):
    interaction: bool
    target: Optional[str] = Field(default=None, description="Shared target of drugs")

class DDIResponse(BaseModel):
    interaction: bool
    conditions_and_prr: Optional[dict[str, float]] = Field(default=None, description="Condition : PRR dictionary")

# Target Preprocessing
shared_targets = target_df.groupby(['Target', 'Target ID'])['Ligand'].apply(lambda x: set(l.lower() for l in x)).reset_index()

# TWOSIDES Preprocessing
twosides_df["drug_1_concept_name"] = twosides_df["drug_1_concept_name"].str.lower()
twosides_df["drug_2_concept_name"] = twosides_df["drug_2_concept_name"].str.lower()

twosides_df["pair"] = twosides_df.apply(lambda x: frozenset([x["drug_1_concept_name"], x["drug_2_concept_name"]]), axis=1)
twosides_dict = (twosides_df.groupby("pair").apply(lambda x: dict(zip(x["condition_concept_name"], x["PRR"]))).to_dict())

# Return TargetResponse if drugs share a target
@app.get('/check_target/', response_model=TargetResponse)
def check_target(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
                 drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    drug1, drug2 = drug1.lower(), drug2.lower()

    # iterrows() for now due to smaller dataset compared to TWOSIDES
    for _, row in shared_targets.iterrows():
        ligands = row["Ligand"]
        if drug1 in ligands and drug2 in ligands:
            return TargetResponse(
                interaction=True,
                target=row["Target"],
            )

    return TargetResponse(interaction=False)

# Return Conditions and PRR if drugs have a DDI
@app.get('/check_ddi/', response_model=DDIResponse)
def check_ddi(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
              drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    pair = frozenset([drug1.lower(), drug2.lower()])

    conditions_and_prr = twosides_dict.get(pair)
    if conditions_and_prr:
        sorted_conditions_and_prr = dict(sorted(conditions_and_prr.items(), key=lambda items: items[1], reverse=True))
        return DDIResponse(interaction=True, conditions_and_prr=sorted_conditions_and_prr)

    return DDIResponse(interaction=False)