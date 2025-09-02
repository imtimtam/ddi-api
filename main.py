import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional

file_path = "data/interactions.csv"
# Skip header on csv
df = pd.read_csv(file_path, skiprows=1)
app = FastAPI()

class InteractionResponse(BaseModel):
    interaction: bool
    target: Optional[str] = Field(default=None, description="Shared target of drugs")
    description: Optional[str] = Field(default=None, description="Description of effects from interacting drugs")
    severity: Optional[str] = Field(default=None, description="Severity of interacting drugs")


shared_targets = df.groupby(['Target', 'Target ID'])['Ligand'].apply(lambda x: set(l.lower() for l in x)).reset_index()

# Check if input drugs share any same targets
@app.get('/check/', response_model=InteractionResponse)
def check_interaction(drug1: str = Query(..., min_length=2, max_length=50, description="First drug name"),
                      drug2: str = Query(..., min_length=2, max_length=50, description="Second drug name")):
    drug1, drug2 = drug1.lower(), drug2.lower()

    for _, row in shared_targets.iterrows():
        ligands = row["Ligand"]
        if drug1 in ligands and drug2 in ligands:
            return InteractionResponse(
                interaction=True,
                target=row["Target"],
                description=f"{drug1} and {drug2} both act on {row['Target']}, interactions may occur",
                severity="unknown"
            )

    return InteractionResponse(interaction=False)