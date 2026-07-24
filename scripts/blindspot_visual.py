import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


FILE_NAME = "blindspot_risk_master_table.csv"


try:
    df = pd.read_csv(FILE_NAME)
except Exception:
    df = pd.read_csv(FILE_NAME, sep="\t")


df.columns = [str(c).strip() for c in df.columns]


df_clean = df[['country_name', 'blindspot_risk_score']].dropna().copy()
df_clean['blindspot_risk_score'] = pd.to_numeric(df_clean['blindspot_risk_score'], errors='coerce')


df_sorted = df_clean.sort_values(by='blindspot_risk_score', ascending=True)


print("Generating 3D Rotatable Globe...")

fig_map = px.choropleth(
    df_clean,
    locations="country_name",
    locationmode="country names",
    color="blindspot_risk_score",
    hover_name="country_name",
    color_continuous_scale="Blues", 
    range_color=(0, 1),
    title="<b>Global Blind Spot Risk Score (Interactive 3D Globe)</b>",
    labels={'blindspot_risk_score': 'Risk Score', 'country_name': 'Country'}
)


fig_map.update_geos(
    projection_type="orthographic",  
    showcoastlines=True,
    coastlinecolor="lightgrey",
    showland=True,
    landcolor="#FFFFFF",            
    showocean=True,
    oceancolor="#0E1117",          
    showlakes=False
)

fig_map.update_layout(
    paper_bgcolor="#0E1117",       
    font=dict(color="white"),       
    margin={"r":0, "t":50, "l":0, "b":0},
    coloraxis_colorbar=dict(
        title=dict(
            text="Risk Score",
            font=dict(color="white") 
        ),
        tickfont=dict(color="white")
    )
)


fig_map.write_html("blindspot_risk_globe.html")
fig_map.show()


print("Generating Ranked Bar Chart...")


plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, max(6, len(df_sorted) * 0.4)))  # Dynamic height based on number of countries


norm = plt.Normalize(0, 1)
cmap = plt.cm.Blues


bars = ax.barh(
    df_sorted['country_name'], 
    df_sorted['blindspot_risk_score'], 
    color=cmap(norm(df_sorted['blindspot_risk_score']))
)


for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.01, 
        bar.get_y() + bar.get_height()/2, 
        f"{width:.4f}", 
        va='center', 
        ha='left', 
        color='white', 
        fontsize=10, 
        fontweight='bold'
    )


ax.set_title('Blind Spot Risk Score by Country', fontsize=14, fontweight='bold', pad=15, color='white')
ax.set_xlabel('Blind Spot Risk Score (0 - 1)', fontsize=12, color='white')
ax.set_ylabel('Country', fontsize=12, color='white')
ax.set_xlim(0, 1.1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig("blindspot_risk_barchart.png", dpi=300)
plt.show()

print("✅ Done! Map saved to 'blindspot_risk_globe.html' and bar chart saved to 'blindspot_risk_barchart.png'.")