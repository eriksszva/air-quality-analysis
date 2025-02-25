import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

sns.set(style='dark')
df = pd.read_csv('dashboard/main.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index)

# Menambahkan filter interaktif
st.sidebar.header("Filter Data")
selected_date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [df.index.min(), df.index.max()])
selected_station = st.sidebar.multiselect("Pilih Stasiun", df['station'].unique(), df['station'].unique())

# Filter dataset berdasarkan input pengguna
filtered_df = df[(df.index >= pd.to_datetime(selected_date_range[0])) & (df.index <= pd.to_datetime(selected_date_range[1]))]
filtered_df = filtered_df[filtered_df['station'].isin(selected_station)]

st.header('Analisis Kualitas Udara: Konsentrasi PM2.5 dan PM10 dalam Kurun Waktu 5 Tahun')
st.subheader('Mengeksplor Faktor Meteorologis, Kategori Kualitas Udara, dan Pola Waktu')
col1, col2, col3 = st.columns(3)

with col1:
    total_station = filtered_df['station'].nunique()
    st.metric('**Total Stasiun**', value=f'{total_station} stasiun')

with col2:
    avg_pm10 = filtered_df['PM10'].mean()
    st.metric('**Rata-Rata PM10**', value=f'{avg_pm10:.2f} µg/m³')

with col3:
    avg_pm25 = filtered_df['PM2.5'].mean()
    st.metric('**Rata-Rata PM2.5**', value=f'{avg_pm25:.2f} µg/m³')



# Membuat scatter plot
sampled_df = filtered_df[['PM2.5', 'PM10', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']].sample(n=min(10000, len(filtered_df)), random_state=42)
meteorology_vars = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
pollutants = ['PM2.5', 'PM10']

fig, axes = plt.subplots(nrows=2, ncols=len(meteorology_vars), figsize=(15, 8), sharey='row')
for i, pol in enumerate(pollutants):
    for j, met in enumerate(meteorology_vars):
        ax = axes[i, j]
        sns.scatterplot(data=sampled_df, x=met, y=pol, alpha=0.3, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(pol if j == 0 else "")
        ax.set_title(met)
plt.suptitle('Hubungan Linear Antara PM2.5 & PM10 vs Faktor Meteorologis', fontsize=14, y=1.05)
plt.tight_layout()
st.pyplot(fig)



# Membuat tren bulanan
st.subheader('Rata-Rata Bulanan Konsentrasi PM2.5 dan PM10')
def create_monthly_trend(data):
    data['year'] = data.index.year
    data['month'] = data.index.month
    return data.groupby(['year', 'month'])[['PM2.5', 'PM10']].mean().reset_index()

monthly_df = create_monthly_trend(filtered_df)

col1, col2 = st.columns(2)
# PM2.5
with col1:
    colors = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=monthly_df, 
        x='month', y='PM2.5', hue='year', 
        palette=colors, dodge=True  
    )
    plt.xticks(ticks=range(0, 12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('')
    plt.ylabel('')
    plt.title('Rata-Rata Bulanan PM2.5')
    plt.legend(loc='upper center', ncol=5, fontsize='small', columnspacing=1.0, handletextpad=0.5)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

# PM10
with col2:
    colors = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=monthly_df, 
        x='month', y='PM10', hue='year', 
        palette=colors, dodge=True  
    )
    plt.xticks(ticks=range(0, 12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('')
    plt.ylabel('')
    plt.title('Rata-Rata Bulanan PM10')
    plt.legend(loc='upper center', ncol=5, fontsize='small', columnspacing=1.0, handletextpad=0.5)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)



# Heatmap Konsentrasi PM2.5
st.subheader('Korelasi Antara Polutan dan Faktor Meteorologis')
numeric_cols = filtered_df.select_dtypes(exclude='object').columns
corr_matrix = filtered_df[numeric_cols[4:]].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', mask=mask) 
st.pyplot(plt)




# Kategori kualitas udara
st.subheader('Kategori Kualitas Udara Berdasarkan PM2.5 dan PM10')
col1, col2 = st.columns(2)

# Kategori udara berdasarkan PM2.5
with col1:
    air_category_counts = filtered_df['air_category_pm2_5'].value_counts()
    colors = sns.color_palette('Reds', len(air_category_counts))
    plt.figure(figsize=(5, 5))
    plt.pie(
        air_category_counts, labels=air_category_counts.index, autopct='%1.1f%%', textprops={'fontsize': 8} , 
        startangle=90, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )
    centre_circle = plt.Circle((0, 0), 0.40, fc='white')
    plt.gca().add_artist(centre_circle)
    plt.title('Kategori Kualitas Udara Berdasarkan PM2.5')
    st.pyplot(plt)

# Kategori udara berdasarkan PM10
with col2:
    air_category_counts = filtered_df['air_category_pm10'].value_counts()
    colors = sns.color_palette('Blues', len(air_category_counts))
    plt.figure(figsize=(5, 5))
    plt.pie(
        air_category_counts, labels=air_category_counts.index, autopct='%1.1f%%', textprops={'fontsize': 8} ,
        startangle=90, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )
    centre_circle = plt.Circle((0, 0), 0.40, fc='white')
    plt.gca().add_artist(centre_circle)
    plt.title('Kategori Kualitas Udara Berdasarkan PM10')
    st.pyplot(plt)




# Frekuensi Kualitas Udara "Sangat Tidak Sehat" dan "Berbahaya" per Stasiun
st.subheader("Frekuensi Kualitas Udara Sangat Tidak Sehat dan Berbahaya per Stasiun")
severe_air_quality = filtered_df[filtered_df['air_category_pm2_5'].isin(["Sangat Tidak Sehat", "Berbahaya"])]
station_counts = severe_air_quality['station'].value_counts()
plt.figure(figsize=(10, 5))
sns.barplot(x=station_counts.index, y=station_counts.values, color='skyblue')
plt.xticks(rotation=90)
plt.ylabel("Frekuensi")
plt.xlabel("")
plt.title("Frekuensi Kualitas Udara Sangat Tidak Sehat dan Berbahaya per Stasiun")
st.pyplot(plt)


# Waktu kualitas udara memburuk
st.subheader("Waktu Ketika Kualitas Udara Melebihi Tidak Sehat (PM2.5 & PM10 > 35)")
filtered2_df = filtered_df[(filtered_df["PM2.5"] > 35) & (filtered_df["PM10"] > 35)]
time_category_counts = filtered2_df["time_category"].value_counts()
colors = sns.color_palette("Greens", len(time_category_counts))
plt.figure(figsize=(7, 7))
plt.pie(
    time_category_counts, labels=time_category_counts.index, autopct='%1.1f%%',
    startangle=90, colors=colors, wedgeprops={"edgecolor": "white", "linewidth": 1}
)
centre_circle = plt.Circle((0, 0), 0.45, fc="white")
plt.gca().add_artist(centre_circle)
st.pyplot(plt)