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
    

st.header('Analisis Kualitas Udara: Konsentrasi PM2.5 dan PM10 dalam Kurun Waktu 5 Tahun')
st.subheader('Mengeksplor Faktor Meteorologis, Kategori Kualitas Udara, dan Pola Waktu')
col1, col2, col3 = st.columns(3)

with col1:
    total_station = df['station'].nunique()
    st.metric('**Total Stasiun**', value=f'{total_station} stasiun')

with col2:
    avg_pm25 = df['PM10'].mean()
    st.metric('**Rata-Rata PM10**', value=f'{avg_pm25:.2f} µg/m³')

with col3:
    avg_pm25 = df['PM2.5'].mean()
    st.metric('**Rata-Rata PM2.5**', value=f'{avg_pm25:.2f} µg/m³')


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
st.markdown("""
        PM2.5 dan PM10 menunjukkan korelasi linear positif dengan DEWP, di mana peningkatan titik embun berhubungan dengan meningkatnya konsentrasi partikel polutan. Scatter plot menunjukkan pola linear ini, meskipun sebagian besar nilai terkonsentrasi di bawah 400 µg/m³. Peningkatan titik embun dapat memengaruhi proses kondensasi dan adsorpsi partikel polutan di udara, sehingga berkontribusi pada konsentrasi polutan yang lebih tinggi.  

        Sementara itu, PM2.5 dan PM10 memiliki korelasi linear negatif dengan WSPM, di mana semakin tinggi kecepatan angin, semakin rendah konsentrasi polutan. Scatter plot menunjukkan bahwa angin berperan dalam penyebaran polutan dengan menentukan arah dan seberapa jauh pencemar terbawa. Menurut penelitian Hakiki (2008), peningkatan kecepatan angin mempercepat penyebaran polutan, menyebabkan konsentrasinya lebih rendah di area yang lebih jauh dari sumber pencemaran.   
""")


# membuat heatmap 
st.subheader('Korelasi Antara Polutan dan Faktor Meteorologis')
numeric_cols = df.select_dtypes(exclude='object').columns
correlation_matrix, mask = create_heatmap(df, numeric_cols)

plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', mask=mask) 
st.pyplot(plt)
st.markdown("""
        Faktor meteorologis memiliki hubungan yang erat dengan polutan seperti PM2.5, PM10, CO, SO2, dan NO2. CO menunjukkan korelasi kuat dengan PM2.5 (0.77), PM10 (0.69), SO2 (0.52), dan NO2 (0.69), menunjukkan bahwa CO berperan dalam peningkatan polusi udara. NO2 juga memiliki hubungan signifikan dengan PM2.5 (0.66), PM10 (0.65), dan SO2 (0.49), mengindikasikan bahwa NO2 berkontribusi pada peningkatan polutan lainnya. Faktor meteorologis seperti tekanan udara (PRES) juga berpengaruh terhadap polutan, di mana peningkatan tekanan udara berkaitan dengan perubahan kadar SO2, NO2, dan CO.
""")


# membuat trend tahunan
st.subheader('Rata-Rata Tahunan Konsentrasi PM2.5 dan PM10')
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
plt.legend(title='Polutan', loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(plt)
st.markdown("""
        Partikel polutan PM2.5 dan PM10 mengalami fluktuasi signifikan dari tahun ke tahun. Terlihat lonjakan rata-rata konsentrasi kedua polutan pada tahun 2014 dibandingkan dengan 2013, yang kemudian diikuti oleh tren penurunan hingga mencapai titik terendah pada 2016. Namun, pada 2017, terjadi peningkatan kembali dalam konsentrasi PM2.5 dan PM10, meskipun pencatatan data di tahun tersebut baru mencakup hingga bulan Februari. Hal ini dapat mengindikasikan adanya faktor musiman atau perubahan aktivitas industri dan lingkungan yang memengaruhi kadar polutan di udara.
""")


# membuat trend bulanan
st.subheader('Rata-Rata Bulanan Konsentrasi PM2.5 dan PM10')
monthly_df = create_monthly_trend(df)
col1, col2 = st.columns(2)
# PM2.5
with col1:
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

with col2:
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

st.markdown("""
        Rata-rata konsentrasi PM2.5 dan PM10 dalam rentang tahun 2013–2017 menunjukkan pola musiman yang serupa. Konsentrasi cenderung meningkat pada Februari hingga Maret, lalu menurun bertahap hingga Agustus. Setelah itu, terjadi peningkatan kembali mulai Oktober, dengan puncak tertinggi pada Desember. Pola ini menunjukkan adanya faktor musiman yang memengaruhi fluktuasi polusi udara, seperti perubahan cuaca, curah hujan, serta aktivitas manusia.  

        Kenaikan konsentrasi PM2.5 dan PM10 pada akhir tahun kemungkinan dipengaruhi oleh meningkatnya aktivitas industri, pembakaran biomassa, dan faktor meteorologi seperti kelembapan serta kecepatan angin yang memengaruhi penyebaran polutan. Sementara itu, penurunan konsentrasi pada pertengahan tahun bisa dikaitkan dengan meningkatnya curah hujan yang membantu membersihkan udara dari partikel polutan.
""")


st.subheader('Kategori Kualitas Udara Berdasarkan PM2.5 dan PM10')
col1, col2 = st.columns(2)
# kategori udara berdasarkan PM2.5
with col1:
    air_category_counts = df['air_category_pm2_5'].value_counts()
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

# kategori udara berdasarkan PM10
with col2:
    air_category_counts = df['air_category_pm10'].value_counts()
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

st.markdown("""
        Berdasarkan hasil pencatatan selama lima tahun (2013–2017) di 12 stasiun pengukuran, kualitas udara sering kali berada pada tingkat yang tidak sehat untuk dihirup langsung, baik akibat konsentrasi PM2.5 maupun PM10.

        Untuk PM2.5, kategori udara yang paling sering terjadi adalah "tidak sehat" (33,8%), diikuti oleh "sedang" (21,6%), "baik" (14,9%), "tidak sehat bagi kelompok sensitif" (14,7%), serta "sangat tidak sehat" dan "berbahaya" dalam persentase yang lebih kecil. Konsentrasi PM2.5 yang tinggi berpotensi membahayakan kesehatan dan meningkatkan risiko gangguan pernapasan.

        Sementara itu, untuk PM10, kategori udara yang paling sering terjadi juga adalah "tidak sehat" (40,9%), diikuti oleh "sedang" (17,8%), "sangat tidak sehat" (16,2%), serta kategori lain dalam persentase lebih kecil. Jika dibandingkan, konsentrasi PM10 lebih sering menunjukkan kategori "tidak sehat", yang mengindikasikan bahwa PM10 dapat memiliki dampak kesehatan yang lebih berbahaya dibandingkan PM2.5.

        Secara keseluruhan, tingginya konsentrasi PM2.5 dan PM10 dalam udara menunjukkan bahwa partikel-partikel ini berpotensi membahayakan kesehatan dan meningkatkan risiko gangguan pernapasan.
""")


# menampilkan stasiun dengan kualitas udara terburuk
kategori_buruk = ['Sangat Tidak Sehat', 'Berbahaya'] 

filtered_df = df[
    (df['air_category_pm2_5'].isin(kategori_buruk)) | 
    (df['air_category_pm10'].isin(kategori_buruk))
]
# group by setelah filtering
station_count = filtered_df.groupby('station').size().reset_index(name='count')
station_count = station_count.sort_values(by='count', ascending=False).reset_index(drop=True)
st.subheader('Frekuensi Kualitas Udara Buruk (Sangat Tidak Sehat & Berbahaya) per Stasiun')

# buat layout dua kolom dengan ukuran proporsional
col1, col2 = st.columns([1, 2])

# tampilkan DataFrame di kolom pertama
with col1:
    st.write('Frekuensi dalam Tabel:')
    st.dataframe(station_count.set_index('station'))

# tampilkan barchart di kolom kedua
with col2:
    st.write('Frekuensi Kualitas Udara Sangat Tidak Sehat dan Berbahaya per Stasiun')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(station_count['station'], station_count['count'], color='skyblue')
    
    # tambahkan label
    ax.set_xlabel('')
    ax.set_ylabel('Count', fontsize=12)
    #ax.set_title('Jumlah Kategori Buruk per Stasiun', fontsize=14, fontweight='bold')
    ax.set_xticklabels(station_count['station'], rotation=45, ha='right')
    st.pyplot(fig)

st.markdown("""
        Stasiun yang sering mencatat kategori "sangat tidak sehat" dan "berbahaya" adalah Gucheng, Wanliu, Wanshouxigong, Aotizhongxin, dan Dongsi. Faktor geografis dan aktivitas manusia di sekitar stasiun dapat mempengaruhi tingkat polusi udara yang tercatat. Konsentrasi PM2.5 dan PM10 di stasiun-stasiun ini sering kali melebihi ambang batas kesehatan. Penyebab utama dapat berasal dari transportasi, aktivitas industri, dan kondisi atmosfer yang memperburuk penyebaran polutan.
""")



# waktu kualitas udara memburuk
st.subheader('Waktu Ketika Kualitas Udara Melebihi Tidak Sehat (PM2.5 & PM10 > 35)')
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
st.pyplot(plt)
st.markdown("""
        Kualitas udara yang mulai tidak baik bagi kelompok sensitif hingga mencapai kategori berbahaya lebih sering terjadi pada malam hari, diikuti oleh pagi dan siang hari. Berdasarkan output dari multivariate analysis dengan heatmap maka: 
        - Pada malam hari, kondisi atmosfer cenderung stabil dengan suhu yang lebih rendah dan kecepatan angin yang lebih lemah. Hal ini menyebabkan polutan seperti PM2.5, PM10, CO, dan NO2 terperangkap di lapisan udara yang lebih dekat ke permukaan tanah, sehingga akan meningkatkan konsentrasinya dan mempengaruhi kualitas udara.  
        - Pada pagi hari, peningkatan aktivitas manusia seperti lalu lintas kendaraan bermotor, pembakaran biomassa, serta aktivitas industri dan pabrik mulai berkontribusi terhadap peningkatan kadar polutan. Selain itu, kondisi embun (DEWP) yang tinggi di pagi hari dapat memperburuk penumpukan polutan.  
        - Pada siang hari, meskipun aktivitas industri dan transportasi masih tinggi, meningkatnya suhu udara (TEMP) dan kecepatan angin (WSPM) dapat membantu menyebarkan polutan ke lapisan atmosfer yang lebih tinggi, mengurangi konsentrasi di dekat permukaan. Namun, peningkatan suhu juga dapat mempercepat reaksi kimia yang menghasilkan ozon (O3), yang dapat berkontribusi terhadap penurunan kualitas udara.  
""")


st.markdown("""
        ### **Kesimpulan**

        Faktor meteorologis memiliki pengaruh signifikan terhadap polusi udara, dengan CO dan NO2 menunjukkan korelasi kuat terhadap PM2.5, PM10, dan SO2. Tekanan udara, titik embun, serta kecepatan dan arah angin juga berperan dalam penyebaran polutan. Konsentrasi PM2.5 dan PM10 mengalami fluktuasi tahunan dengan lonjakan pada 2014 dan tren menurun hingga 2016, sebelum meningkat kembali pada 2017. Secara musiman, konsentrasi polutan cenderung lebih tinggi di awal dan akhir tahun, dipengaruhi oleh curah hujan, kelembaban, dan aktivitas manusia. Kualitas udara sering kali berada dalam kategori "tidak sehat," dengan beberapa stasiun seperti Gucheng dan Wanliu mencatat tingkat polusi tertinggi akibat faktor geografis dan aktivitas industri. Polusi udara cenderung lebih buruk pada malam hari karena atmosfer lebih stabil, suhu lebih rendah, dan angin lebih lemah, menyebabkan polutan terperangkap di lapisan bawah.
""")

