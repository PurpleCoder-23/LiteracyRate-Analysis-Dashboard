import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd

st.set_page_config(layout="wide")

st.title("Indian Literacy Rate Analysis Dashboard (2001-2011)")

@st.cache_data
def load_data():
    df = pd.read_csv("GOI.csv")
    df = df.rename(columns={
        "Country/ States/ Union Territories Name": "ST_NM",
        "Literacy Rate (Persons) - Total - 2001": "Total Literacy Rate in 2001",
        "Literacy Rate (Persons) - Total - 2011": "Total Literacy Rate in 2011",
        "Literacy Rate (Persons) - Rural - 2001": "Rural Literacy Rate in 2001",
        "Literacy Rate (Persons) - Rural - 2011": "Rural Literacy Rate in 2011",
        "Literacy Rate (Persons) - Urban - 2001": "Urban Literacy Rate in 2001",
        "Literacy Rate (Persons) - Urban - 2011": "Urban Literacy Rate in 2011"
    })
    df['Total Growth Rate'] = ((df['Total Literacy Rate in 2011'] - df['Total Literacy Rate in 2001']) / df['Total Literacy Rate in 2001']) * 100
    df['Rural Growth Rate'] = ((df['Rural Literacy Rate in 2011'] - df['Rural Literacy Rate in 2001']) / df['Rural Literacy Rate in 2001']) * 100
    df['Urban Growth Rate'] = ((df['Urban Literacy Rate in 2011'] - df['Urban Literacy Rate in 2001']) / df['Urban Literacy Rate in 2001']) * 100
    if 'Category' not in df.columns:
        df['Category'] = 'All'
    return df

df = load_data()

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
    gdf = gpd.read_file(url)
    gdf["geometry"] = gdf.to_crs(gdf.estimate_utm_crs()).simplify(1000).to_crs(gdf.crs)
    india_states = gdf.rename(columns={"NAME_1": "ST_NM"}).__geo_interface__
    return india_states

india_states = load_geojson()

# Sidebar filters
st.sidebar.header("Filter Options")

selected_category = st.sidebar.multiselect(
    "Filter by Category",
    df['Category'].unique(),
    default=df['Category'].unique()
)

min_literacy = st.sidebar.slider(
    "Minimum Total Literacy Rate (2011)",
    min_value=float(df['Total Literacy Rate in 2011'].min()),
    max_value=float(df['Total Literacy Rate in 2011'].max()),
    value=float(df['Total Literacy Rate in 2011'].min())
)

# Move pie chart to sidebar
st.sidebar.header("Category Distribution")
category_counts = df['Category'].value_counts()
labels = category_counts.index
sizes = category_counts.values
colors = sns.color_palette('Dark2', n_colors=len(labels))
fig_pie, ax_pie = plt.subplots(figsize=(4, 4))
ax_pie.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct='%.1f%%',
    startangle=90,
    pctdistance=0.85,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1}
)
ax_pie.axis('equal')
ax_pie.set_title('Distribution of Categories', fontsize=14)
st.sidebar.pyplot(fig_pie)

filtered_df = df[
    (df['Category'].isin(selected_category)) &
    (df['Total Literacy Rate in 2011'] >= min_literacy)
]

st.subheader("Overview of Data")
st.dataframe(filtered_df.head())

# Choropleth maps (wider size)
st.header("Literacy Rate Distribution Across India (2001 & 2011)")
col1, col2 = st.columns([1.1, 1.1])  # slightly wider

with col1:
    st.subheader("Choropleth Total Literacy Rate in 2001")
    fig_2001 = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',
        locations='ST_NM',
        color='Total Literacy Rate in 2001',
        color_continuous_scale="Viridis",
        range_color=(df['Total Literacy Rate in 2001'].min(), df['Total Literacy Rate in 2001'].max()),
        scope="asia",
        labels={'Total Literacy Rate in 2001': 'Total Literacy Rate (2001)'}
    )
    fig_2001.update_geos(visible=True, projection_type="mercator", fitbounds="locations")
    fig_2001.update_layout(title_text='Density Map of Total Literacy Rate in India (2001)', title_x=0.5, margin={"r":0,"t":60,"l":0,"b":0}, height=600)
    st.plotly_chart(fig_2001, use_container_width=True)

with col2:
    st.subheader("Choropleth Total Literacy Rate in 2011")
    fig_2011 = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',
        locations='ST_NM',
        color='Total Literacy Rate in 2011',
        color_continuous_scale="Plasma",
        range_color=(df['Total Literacy Rate in 2011'].min(), df['Total Literacy Rate in 2011'].max()),
        scope="asia",
        labels={'Total Literacy Rate in 2011': 'Total Literacy Rate (2011)'}
    )
    fig_2011.update_geos(visible=True, projection_type="mercator", fitbounds="locations")
    fig_2011.update_layout(title_text='Density Map of Total Literacy Rate in India (2011)', title_x=0.5, margin={"r":0,"t":60,"l":0,"b":0}, height=600)
    st.plotly_chart(fig_2011, use_container_width=True)

# Helper function for bar charts (increased size)
def create_horizontal_bar_chart(data, x_col, y_col, title, hue_col=None, palette='viridis'):
    plt.figure(figsize=(14, 12))  # bigger figure
    if isinstance(x_col, list) and hue_col:
        df_melted = data.melt(
            id_vars=[y_col],
            value_vars=x_col,
            var_name="Year",
            value_name="Literacy Rate"
        )
        year_map = {x_col[0]: "2001", x_col[1]: "2011"}
        df_melted['Year'] = df_melted['Year'].map(year_map)
        ax = sns.barplot(
            x="Literacy Rate",
            y=y_col,
            hue="Year",
            data=df_melted.sort_values(by="Literacy Rate", ascending=True),
            palette=palette
        )
        plt.xlim(0, 100)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontsize=10, color='black')
        plt.legend(title='Year', fontsize=12, title_fontsize=14, bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    else:
        ax = sns.barplot(
            x=x_col,
            y=y_col,
            data=data.sort_values(by=x_col, ascending=True),
            palette=palette
        )
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', padding=3, fontsize=10, color='black')

    plt.title(title, fontsize=18)
    xlabel = "Literacy Rate (%)" if isinstance(x_col, list) else f'{x_col.replace(" Rate", " Rate (%)")}'
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(y_col, fontsize=14)
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return plt

# Total Literacy and Growth Rate Bar Charts + insights below each graph
st.header("Total Literacy and Growth Rates")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Literacy Rate (2001 vs 2011)")
    fig_total_literacy = create_horizontal_bar_chart(
        filtered_df,
        x_col=["Total Literacy Rate in 2001", "Total Literacy Rate in 2011"],
        y_col="ST_NM",
        title="Total Literacy Rate in Indian States/UTs (2001 vs 2011)",
        hue_col="Year",
        palette='viridis'
    )
    st.pyplot(fig_total_literacy)
    st.markdown(
        "<small>"
        "* Bihar consistently recorded the lowest literacy rate (40-60%).<br>"
        "* Kerala maintained the highest literacy rate (~90-95%).<br>"
        "* Mizoram saw smallest growth (2.8%), Dadra & Nagar Haveli highest (32%), Bihar second highest (31.5%)."
        "</small>",
        unsafe_allow_html=True
    )

with col2:
    st.subheader("Total Growth Rate (2001-2011)")
    fig_total_growth = create_horizontal_bar_chart(
        filtered_df,
        x_col="Total Growth Rate",
        y_col="ST_NM",
        title="Total Literacy Growth Rate in Indian States/UTs (2001-2011)",
        palette="coolwarm"
    )
    st.pyplot(fig_total_growth)

# Rural Literacy and Growth Rate Bar Charts + insights
st.header("Rural Literacy and Growth Rates")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rural Literacy Rate (2001 vs 2011)")
    fig_rural_literacy = create_horizontal_bar_chart(
        filtered_df,
        x_col=["Rural Literacy Rate in 2001", "Rural Literacy Rate in 2011"],
        y_col="ST_NM",
        title="Rural Literacy Rate in Indian States/UTs (2001 vs 2011)",
        hue_col="Year",
        palette='tab10'
    )
    st.pyplot(fig_rural_literacy)
    st.markdown(
        "<small>"
        "* Bihar had lowest rural literacy (40-60%).<br>"
        "* Kerala led rural literacy (~90-93%).<br>"
        "* Kerala growth modest (3.3%), Bihar highest growth (36.2%)."
        "</small>",
        unsafe_allow_html=True
    )

with col4:
    st.subheader("Rural Growth Rate (2001-2011)")
    fig_rural_growth = create_horizontal_bar_chart(
        filtered_df,
        x_col="Rural Growth Rate",
        y_col="ST_NM",
        title="Rural Literacy Growth Rate in Indian States/UTs (2001-2011)",
        palette="Set2"
    )
    st.pyplot(fig_rural_growth)

# Urban Literacy and Growth Rate Bar Charts + insights
st.header("Urban Literacy and Growth Rates")
col5, col6 = st.columns(2)

with col5:
    st.subheader("Urban Literacy Rate (2001 vs 2011)")
    fig_urban_literacy = create_horizontal_bar_chart(
        filtered_df,
        x_col=["Urban Literacy Rate in 2001", "Urban Literacy Rate in 2011"],
        y_col="ST_NM",
        title="Urban Literacy Rate in Indian States/UTs (2001 vs 2011)",
        hue_col="Year",
        palette='Paired'
    )
    st.pyplot(fig_urban_literacy)
    st.markdown(
        "<small>"
        "* 2001: Uttar Pradesh lowest urban literacy (69%).<br>"
        "* 2011: Bihar lowest (75%).<br>"
        "* Mizoram led urban literacy (96-97%).<br>"
        "* Mizoram & Kerala had minimal growth, Manipur & Daman & Diu highest (8%)."
        "</small>",
        unsafe_allow_html=True
    )

with col6:
    st.subheader("Urban Growth Rate (2001-2011)")
    fig_urban_growth = create_horizontal_bar_chart(
        filtered_df,
        x_col="Urban Growth Rate",
        y_col="ST_NM",
        title="Urban Literacy Growth Rate in Indian States/UTs (2001-2011)",
        palette="Set1"
    )
    st.pyplot(fig_urban_growth)

# Scatter plots for Rural vs Urban Literacy Rates 2001 and 2011 (keep as is, maybe a bit bigger)
st.subheader("Rural vs Urban Literacy Rates (Scatter Plots)")
col7, col8 = st.columns(2)

with col7:
    fig_scatter_2001, ax_2001 = plt.subplots(figsize=(8, 8))
    sns.scatterplot(
        data=df,
        x='Rural Literacy Rate in 2001',
        y='Urban Literacy Rate in 2001',
        hue='Category',
        s=100,
        palette='deep',
        ax=ax_2001
    )
    ax_2001.set_title("Rural vs Urban Literacy Rates (2001)", fontsize=16)
    ax_2001.set_xlim(30, 100)
    ax_2001.set_ylim(30, 100)
    ax_2001.set_xlabel("Rural Literacy Rate (2001)")
    ax_2001.set_ylabel("Urban Literacy Rate (2001)")
    ax_2001.grid(True)
    st.pyplot(fig_scatter_2001)

with col8:
    fig_scatter_2011, ax_2011 = plt.subplots(figsize=(8, 8))
    sns.scatterplot(
        data=df,
        x='Rural Literacy Rate in 2011',
        y='Urban Literacy Rate in 2011',
        hue='Category',
        s=100,
        palette='deep',
        ax=ax_2011
    )
    ax_2011.set_title("Rural vs Urban Literacy Rates (2011)", fontsize=16)
    ax_2011.set_xlim(30, 100)
    ax_2011.set_ylim(30, 100)
    ax_2011.set_xlabel("Rural Literacy Rate (2011)")
    ax_2011.set_ylabel("Urban Literacy Rate (2011)")
    ax_2011.grid(True)
    st.pyplot(fig_scatter_2011)

st.markdown("---")
st.caption("Dashboard created using Streamlit, Plotly Express, Seaborn, and Geopandas.")
