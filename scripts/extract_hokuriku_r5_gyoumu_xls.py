from pathlib import Path
import pandas as pd
import json
from datetime import datetime, date

src = Path("data/mlit_r5_confirmed/hokuriku_r5_gyoumu_2023.xls")
out = Path("data/mlit_r5_confirmed/hokuriku_r5_gyoumu_contracts.json")

df = pd.read_excel(src, header=None)

def conv(v):
    if pd.isna(v):
        return None
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return v

records = []

for _, row in df.iloc[4:].iterrows():

    if pd.isna(row[1]):
        continue

    remarks = conv(row[21])

    if remarks not in ["落札", "決定"]:
        continue

    records.append({
        "bureau": "北陸地方整備局",
        "fiscal_year": "R5",
        "month": "2023-04_to_2024-03",
        "category": "業務",
        "source_type": "excel",

        "department": conv(row[0]),
        "project_name": conv(row[1]),
        "bid_date": conv(row[2]),
        "contract_date": conv(row[3]),
        "work_type": conv(row[4]),
        "bid_method": conv(row[5]),
        "comprehensive_evaluation": conv(row[6]),
        "bidder": conv(row[7]),

        "planned_price_ex_tax": conv(row[8]),
        "investigation_base_price_ex_tax": conv(row[9]),
        "technical_score": conv(row[10]),

        "bid_amount_1st_ex_tax": conv(row[11]),
        "price_score_1st": conv(row[12]),
        "evaluation_value_1st": conv(row[13]),

        "bid_amount_2nd_ex_tax": conv(row[14]),
        "price_score_2nd": conv(row[15]),
        "evaluation_value_2nd": conv(row[16]),

        "bid_amount_3rd_ex_tax": conv(row[17]),
        "price_score_3rd": conv(row[18]),
        "evaluation_value_3rd": conv(row[19]),

        "estimate_amount_ex_tax": conv(row[20]),
        "remarks": remarks,

        "unit_or_total": conv(row[22]),

        "is_awarded": True,
    })

out.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("saved:", out)
print("count:", len(records))
