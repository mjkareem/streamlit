import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Gapminder')
st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")

# Load Data
@st.cache_data
def load_data():
    # Convert M notation to float
    def convert_to_number(x):
        if 'B' in str(x):
            return float(x.replace('B', '')) * 1e9
        elif 'M' in str(x):
            return float(x.replace('M', '')) * 1e6
        elif 'k' in str(x):
            return float(x.replace('k', '')) * 1e3
        else:
            return float(x)

    # Load each dataset
    df_life_exp = pd.read_csv('lex.csv')
    df_population = pd.read_csv('pop.csv')
    df_gni = pd.read_csv('ny_gnp_pcap_pp_cd.csv')

    # Transform to tidy format
    df_life_exp = df_life_exp.melt(id_vars=['country'], var_name='year', value_name='life_expectancy')
    df_population = df_population.melt(id_vars=['country'], var_name='year', value_name='population')
    df_gni = df_gni.melt(id_vars=['country'], var_name='year', value_name='gni_per_capita')

    # Forward fill missing data
    df_life_exp = df_life_exp.sort_values(['country', 'year']).ffill()
    df_population = df_population.sort_values(['country', 'year']).ffill()
    df_gni = df_gni.sort_values(['country', 'year']).ffill()

    # Merge into single dataframe
    df = pd.merge(df_life_exp, df_population, on=['country', 'year'])
    df = pd.merge(df, df_gni, on=['country', 'year'])

    df['year'] = df['year'].astype(int)  # Ensure 'year' is integer type
    # Ensure 'population', 'life_expectancy' and 'gni_per_capita' are float type
    df['population'] = df['population'].apply(convert_to_number)
    df['life_expectancy'] = df['life_expectancy'].astype(float)
    df['gni_per_capita'] = df['gni_per_capita'].apply(convert_to_number)

    return df

df = load_data()

# Continue with the rest of the code as before


# Sidebar
st.sidebar.title("Controls")
selected_year = st.sidebar.slider("Select Year", min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=int(df['year'].max()))
selected_countries = st.sidebar.multiselect("Select Countries", options=list(df['country'].unique()))

# Filter dataframe based on controls
df_filtered = df[(df['country'].isin(selected_countries)) & (df['year'] == selected_year)]

# Plot
st.title(f"Life Expectancy, Population and GNI per Capita for Selected Countries in {selected_year}")
fig = px.scatter(df_filtered,
                 x="gni_per_capita",
                 y="life_expectancy",
                 size="population",
                 color="country",
                 log_x=True,  # Logarithmic scale for x-axis
                 hover_name="country",
                 size_max=60)

st.plotly_chart(fig)