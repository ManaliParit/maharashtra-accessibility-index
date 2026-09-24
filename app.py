
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import requests

st.set_page_config(
    page_title="Maharashtra Accessibility Index",
    layout="wide"
)

st.title("Maharashtra Accessibility Index")
st.write("District-wise Accessibility Index")

# -----------------------------
# 1. Accessibility data
# -----------------------------
df = pd.read_csv("accessibility_data.csv")

# -----------------------------
# 2. District name mapping
# -----------------------------
name_mapping = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

df["district_map"] = df["district"].replace(name_mapping)

# -----------------------------
# 3. Rank
# -----------------------------
df["Rank"] = (
    df["accessibility_score"]
    .rank(method="first", ascending=False)
    .astype(int)
)

# -----------------------------
# 4. Maharashtra GeoJSON
# -----------------------------
url = "https://gist.githubusercontent.com/saketkc/7c1ce9d993773ced9974f6c57730b7df/raw/Maharashtra.geojson"

response = requests.get(url, timeout=30)

with open("maharashtra_latest.geojson", "wb") as f:
    f.write(response.content)

maha_latest = gpd.read_file("maharashtra_latest.geojson")

# -----------------------------
# 5. Merge data with map
# -----------------------------
merged_latest = maha_latest.merge(
    df,
    left_on="dtname",
    right_on="district_map",
    how="left"
)

# -----------------------------
# 6. Colour function
# -----------------------------
def get_color(value):

    if pd.isna(value):
        return "lightgray"

    elif value <= 0.30:
        return "red"

    elif value <= 0.50:
        return "orange"

    else:
        return "green"

# -----------------------------
# 7. Maharashtra map
# -----------------------------
m = folium.Map(
    location=[19.75, 75.70],
    zoom_start=6,
    tiles=None
)

# -----------------------------
# 8. District polygons
# -----------------------------
folium.GeoJson(
    merged_latest,
    style_function=lambda feature: {
        "fillColor": get_color(
            feature["properties"]["accessibility_score"]
        ),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7
    },
    tooltip=GeoJsonTooltip(
        fields=[
            "dtname",
            "accessibility_score",
            "Rank"
        ],
        aliases=[
            "District:",
            "Accessibility Score:",
            "Rank:"
        ],
        localize=True
    )
).add_to(m)

# -----------------------------
# 9. Legend
# -----------------------------
legend_html = """
<div style="
    position: fixed;
    bottom: 40px;
    right: 20px;
    width: 220px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    font-size: 14px;
    padding: 10px;
">

<b>Accessibility Score</b>
<br><br>

<i style="
background:red;
width:18px;
height:18px;
display:inline-block;
"></i>
&nbsp; Low (0.10 – 0.30)

<br><br>

<i style="
background:orange;
width:18px;
height:18px;
display:inline-block;
"></i>
&nbsp; Medium (0.31 – 0.50)

<br><br>

<i style="
background:green;
width:18px;
height:18px;
display:inline-block;
"></i>
&nbsp; High (0.51 – 0.78)

<br><br>

<i style="
background:lightgray;
width:18px;
height:18px;
display:inline-block;
"></i>
&nbsp; No Data

</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)

# -----------------------------
# 10. Display map
# -----------------------------
st_folium(
    m,
    width=None,
    height=700
)
