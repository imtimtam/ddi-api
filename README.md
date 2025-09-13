# Drug Interaction and Target Checker API

A **FastAPI** backend service that checks for shared receptor targets and **drug-drug interactions** (DDIs) with associated medical conditions and proportional reporting ratios (PRRs) using the TWOSIDES dataset between two drugs or ligands.

## Features
- **`/check_target`**: Returns whether two drugs share a biological target.  
- **`/check_ddi`**: Returns known interactions between two drugs (condition → PRR mapping).  
- Case-insensitive drug concept name matching.  
- Preprocessing optimizations with frozensets for efficient drug-drug pair lookups.  

## Data Setup
###### Full data files not included in repo due to size despite filtering. Follow **Instructions** below for full set. A smaller test sample will be provided here.
- Drug–Target interactions: `interactions.csv`  
- Drug–Drug Interactions (DDIs): `TWOSIDES_filtered.csv` 
#### Sample Data Instructions
1. Change line 8 of `main.py` to `twosides_path = "data/sample/TWOSIDES_sample.csv"`.

#### Full Data Instructions

1. Download `nsides/TWOSIDES.csv.gz` from the **Data and Source** section on nsides.io.
2. Move `TWOSIDES.csv.gz` to the `data/` folder.
3. Run the notebook `TWOSIDES_analysis.ipynb` to generate `TWOSIDES_trimmed.csv`.

## Getting Started

**1. Clone and move to the repository**

    git clone https://github.com/imtimtam/ddi-api

**2. Install dependencies**

    pip install -r requirements.txt

**3. Run FastAPI with Uvicorn**

    uvicorn main:app --reload

**4. Open browser and navigate to**

    http://127.0.0.1:8000/docs

## Endpoints and Usage

![Swagger UI](images/DDIapi.png)

**1. Check shared target**

**`GET /check_target/`**

**Query Parameters:**

- **drug1** – First drug name

- **drug2** – Second drug name

**Response Example (http://127.0.0.1:8000/check_target/?drug1=asenapine&drug2=apomorphine):**

```
{
  "interaction": true,
  "target": "5-HT<sub>1A</sub> receptor"
}
```

**2. Check drug-drug interaction**

**`GET /check_ddi/`**

**Query Parameters:**

- **drug1** – First drug name

- **drug2** – Second drug name

**Response Example (http://127.0.0.1:8000/full_interactions/?drug1=Diphenhydramine&drug2=Amitriptyline) (truncated):**

```
{
  "interaction": true,
  "targets": [
    "H<sub>1</sub> receptor"
  ],
  "conditions_and_prr": {
    "Onychomycosis": 70,
    "Compression fracture": 70,
    "Diverticulum intestinal": 60,
    "Osteolysis": 60,
    "Osteopenia": 60,
    "Kyphosis": 60,
    "Exposure via ingestion": 55,
    "Hypertensive heart disease": 50,
    "Diabetes mellitus non-insulin-dependent": 50,
    "Dental caries": 50,
    "Cardiotoxicity": 40,
    "Retinopathy": 40,
    "Protein total increased": 40,
    "Cervical spinal stenosis": 40,
    ...
  }
}
```

## License

This project is licensed under the MIT License.

## Credits

- **Guide to Pharmacology** – [https://www.guidetopharmacology.org](https://www.guidetopharmacology.org)  
  Provides information about drug targets and ligand interactions.

- **TWOSIDES Dataset** – [https://www.nsides.io](https://nsides.io/)  
  Contains drug-drug interactions and associated adverse event data.