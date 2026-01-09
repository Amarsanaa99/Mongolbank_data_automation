import pandas as pd
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
output_file = f"mongolbank_data_{today}.csv"

data = {
    "date": [today],
    "status": ["automation test success"]
}

df = pd.DataFrame(data)
df.to_csv(output_file, index=False)

print(f"File created: {output_file}")
