import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st


sns.set(style='dark')
df = pd.read_csv('dashboard/main.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index)

def create_heatmap(df: pd.DataFrame, numeric_cols):
    corr_matrix = df[numeric_cols[4:]].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    return corr_matrix, mask

def create_scatter_plot(df: pd.DataFrame):
    selected_features = ['PM2.5', 'PM10', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    sampled_df = df[selected_features].sample(n=10000, random_state=42)
    meteorology_vars = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    pollutants = ['PM2.5', 'PM10']
    return sampled_df, meteorology_vars, pollutants

def create_yearly_trend(df):
    df_resampled1 = df[['PM10', 'PM2.5']].resample('Y').mean()
    df_yearly_avg = df_resampled1.groupby(df_resampled1.index.year).mean()
    return df_yearly_avg

def create_monthly_trend(df):
    df_resampled2 = df[['PM10', 'PM2.5']].resample('M').mean()
    return df_resampled2
    

st.header('Analisis Konsentrasi PM2.5 dan PM10')
st.subheader('Mengeksplorasi faktor meteorologi dan pola waktu dalam perubahan konsentrasi PM2.5 dan PM10')
col1, col2, col3 = st.columns(3)

with col1:
    total_station = df['station'].nunique()
    st.metric('Total Stasiun', value=total_station)

with col2:
    avg_pm25 = df['PM10'].mean()
    st.metric('Rata-rata PM10', value=f'{avg_pm25:.2f} µg/m³')

with col3:
    avg_pm25 = df['PM2.5'].mean()
    st.metric('Rata-rata PM2.5', value=f'{avg_pm25:.2f} µg/m³')


# membuat scatter plot
sampled_df, meteorology_var, air_pollutant = create_scatter_plot(df)

fig, axes = plt.subplots(nrows=2, ncols=len(meteorology_var), figsize=(15, 8), sharey='row')
for i, pol in enumerate(air_pollutant):
    for j, met in enumerate(meteorology_var):
        ax = axes[i, j]
        sns.scatterplot(data=sampled_df, x=met, y=pol, alpha=0.3, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(pol if j == 0 else "")
        ax.set_title(met)

plt.suptitle('Hubungan Linear Antara PM2.5 & PM10 vs Faktor Meteorologis', fontsize=14, y=1.05)
plt.tight_layout()
st.pyplot(plt)

# membuat heatmap 
numeric_cols = df.select_dtypes(exclude='object').columns
correlation_matrix, mask = create_heatmap(df, numeric_cols)

plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', mask=mask) 
plt.title('Korelasi Antara Polutan dan Faktor Meteorologis')
st.pyplot(plt)

# membuat trend tahunan
yearly_avg = create_yearly_trend(df)

plt.figure(figsize=(9, 6))
# plot garis untuk PM10
sns.lineplot(
    x=yearly_avg.index, 
    y=yearly_avg['PM10'], 
    marker='o', 
    color='royalblue', 
    linewidth=2,
    label='PM10'
)

# plot garis untuk PM2.5
sns.lineplot(
    x=yearly_avg.index, 
    y=yearly_avg['PM2.5'], 
    marker='s', 
    color='crimson', 
    linewidth=2,
    label='PM2.5'
)
# label sumbu
plt.xlabel('')
plt.ylabel('')
plt.title('Rata-Rata Tahunan PM2.5 dan PM10 (2013-2017)')
plt.legend(title='Polutan', loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(plt)

# membuat trend bulanan
monthly_df = create_monthly_trend(df)

# PM2.5
colors = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=monthly_df[['PM2.5']], 
    x=monthly_df.index.month, y='PM2.5', hue=monthly_df.index.year, 
    palette=colors,  
    dodge=True  
)

plt.xticks(ticks=range(0, 12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.xlabel('')
plt.ylabel('')
plt.title('Rata-Rata Bulanan PM2.5 (2013-2017)')
plt.legend(loc='upper center', ncol=5, fontsize='small', columnspacing=1.0, handletextpad=0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(plt)

# PM10
colors = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=monthly_df[['PM10']], 
    x=monthly_df.index.month, y='PM10', hue=monthly_df.index.year, 
    palette=colors,  
    dodge=True  
)

plt.xticks(ticks=range(0, 12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.xlabel('')
plt.ylabel('')
plt.title('Rata-Rata Bulanan PM10 (2013-2017)')
plt.legend(loc='upper center', ncol=5, fontsize='small', columnspacing=1.0, handletextpad=0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(plt)

# kategori udara berdasarkan PM2.5
air_category_counts = df['air_category_pm2_5'].value_counts()
colors = sns.color_palette('Reds', len(air_category_counts))

plt.figure(figsize=(7, 7))

# buat pie chart dengan tengah kosong untuk efek donut
plt.pie(
    air_category_counts, labels=air_category_counts.index, autopct='%1.1f%%',
    startangle=90, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1}
)
# menambahkan lingkaran putih di tengah untuk membuat efek donut
centre_circle = plt.Circle((0, 0), 0.45, fc='white')
plt.gca().add_artist(centre_circle)

plt.title('Kategori Udara Berdasarkan Konsentrasi PM2.5')
st.pyplot(plt)

# kategori udara berdasarkan PM10
air_category_counts = df['air_category_pm10'].value_counts()
colors = sns.color_palette('Blues', len(air_category_counts))

plt.figure(figsize=(7, 7))

# buat pie chart dengan tengah kosong untuk efek donut
plt.pie(
    air_category_counts, labels=air_category_counts.index, autopct='%1.1f%%',
    startangle=90, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1}
)
# menambahkan lingkaran putih di tengah untuk membuat efek donut
centre_circle = plt.Circle((0, 0), 0.45, fc='white')
plt.gca().add_artist(centre_circle)

plt.title('Kategori Udara Berdasarkan Konsentrasi PM10')
st.pyplot(plt)



# menampilkan stasiun dengan kualitas udara terburuk
kategori_buruk = ['Sangat Tidak Sehat', 'Berbahaya'] 

filtered_df = df[
    (df['air_category_pm2_5'].isin(kategori_buruk)) | 
    (df['air_category_pm10'].isin(kategori_buruk))
]
# group by setelah filtering
station_count = filtered_df.groupby('station').size().reset_index(name='count')
station_count = station_count.sort_values(by='count', ascending=False).reset_index(drop=True)
st.subheader('Jumlah kategori buruk per stasiun')

# buat layout dua kolom dengan ukuran proporsional
col1, col2 = st.columns([1, 2])

# tampilkan DataFrame di kolom pertama
with col1:
    st.write('Tabel Stasiun dengan Kategori Buruk')
    st.dataframe(station_count)

# tampilkan barchart di kolom kedua
with col2:
    st.write('Grafik Jumlah Kategori Buruk per Stasiun')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(station_count['station'], station_count['count'], color='skyblue')
    
    # tambahkan label
    ax.set_xlabel('')
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Jumlah Kategori Buruk per Stasiun', fontsize=14, fontweight='bold')
    ax.set_xticklabels(station_count['station'], rotation=45, ha='right')
    st.pyplot(fig)

st.markdown("""
        Stasiun yang sering mencatat kategori "sangat tidak sehat" dan "berbahaya" adalah Gucheng, Wanliu, Wanshouxigong, Aotizhongxin, dan Dongsi. Faktor geografis dan aktivitas manusia di sekitar stasiun dapat mempengaruhi tingkat polusi udara yang tercatat. Konsentrasi PM2.5 dan PM10 di stasiun-stasiun ini sering kali melebihi ambang batas kesehatan. Penyebab utama dapat berasal dari transportasi, aktivitas industri, dan kondisi atmosfer yang memperburuk penyebaran polutan.
""")



# waktu kualitas udara memburuk
filtered_df = df[(df['PM2.5'] > 35) & (df['PM10'] > 35)]

# hitung jumlah kategori waktu
time_category_counts = filtered_df['time_category'].value_counts()

colors = sns.color_palette('Greens', len(time_category_counts))
plt.figure(figsize=(7, 7))
# buat pie chart dengan tengah kosong untuk efek donut
plt.pie(
    time_category_counts, labels=time_category_counts.index, autopct='%1.1f%%',
    startangle=90, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1}
)

# menambahkan lingkaran putih di tengah untuk membuat efek donut
centre_circle = plt.Circle((0, 0), 0.45, fc='white')
plt.gca().add_artist(centre_circle)
plt.title('Kategori Waktu Kualitas Udara Melebihi Tidak Sehat (PM2.5 & PM10 > 35)')
st.pyplot(plt)

st.markdown("""

""")



