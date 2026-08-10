import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="Sistem WIPDASH - Hospital Rompin", page_icon="🏥", layout="wide")

# ==========================================
# 1. KAWALAN KESELAMATAN (PIN)
# ==========================================
PIN_RAHSIA = "7788"

if 'log_masuk' not in st.session_state:
    st.session_state['log_masuk'] = False

if not st.session_state['log_masuk']:
    st.title("🔒 Kawalan Keselamatan WIPDASH")
    st.warning("Sistem ini khas untuk kegunaan Staf Farmasi Hospital Rompin sahaja.")
    pin_input = st.text_input("Sila masukkan PIN Rahsia Staf:", type="password")
    if st.button("Log Masuk", type="primary"):
        if pin_input == PIN_RAHSIA:
            st.session_state['log_masuk'] = True
            st.experimental_rerun()
        else:
            st.error("❌ PIN Salah. Sila cuba lagi.")
    st.stop()

# ==========================================
# 2. INISIALISASI DATA & FUNGSI MASA LIVE
# ==========================================
if 'rekod_data' not in st.session_state:
    st.session_state['rekod_data'] = pd.DataFrame()

# Senarai tahap untuk setiap kategori berdasarkan templat Hospital
tahap_troli = ['Troli Sampai', 'Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap', 'Ambil Bekalan']
tahap_lain = ['Masa Sampai', 'Bekalan Siap', 'Ambil Bekalan']

# Fungsi merekod masa semasa
def set_masa_live(kunci):
    st.session_state[kunci] = datetime.datetime.now().time()

# Pastikan semua kunci masa ada dalam memory
for t in tahap_troli + tahap_lain:
    kunci = f"masa_{t.replace(' ', '_')}"
    if kunci not in st.session_state:
        st.session_state[kunci] = datetime.datetime.now().time()

# ==========================================
# 3. ANTARAMUKA UTAMA
# ==========================================
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🏥 Sistem WIPDASH - Hospital Rompin")
with col_logout:
    st.write("") 
    if st.button("Log Keluar"):
        st.session_state['log_masuk'] = False
        st.experimental_rerun()

st.markdown("**Pemantauan Format Rasmi: Troli Ubat, Floor Stock & Dadah Berbahaya**")

senarai_unit = ['Kenanga 2A', 'Kenanga 2B', 'Kenanga 1A', 'Unit Kecemasan & Trauma', 'Klinik Pakar', 'Unit Hemodialisis']
senarai_kategori = ['Preskripsi Troli Ubat', 'Floor Stock', 'Dadah Berbahaya (DD) / Psikotropik']

tab1, tab2 = st.tabs(["📝 1. Borang Perakam Masa (Punch-In)", "📊 2. Dashboard Analitik"])

# ------------------------------------------
# TAB 1: BORANG KEMASUKAN DATA
# ------------------------------------------
with tab1:
    st.subheader("Borang Kemasukan Rekod Harian")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tarikh = st.date_input("📅 Tarikh Rekod", datetime.date.today())
    with col2:
        kategori = st.selectbox("📂 Pilih Kategori", senarai_kategori)
    with col3:
        unit = st.selectbox("🏥 Pilih Unit / Wad", senarai_unit)
    
    st.markdown("---")
    st.markdown(f"#### ⏱️ Perakam Masa: {kategori}")
    st.caption("Klik butang biru untuk rekod masa semasa. Boleh diubah secara manual jika perlu.")
    
    # Simpanan masa yang dipilih
    masa_dipilih = {}
    
    # LOGIK A: JIKA TROLI UBAT (8 Peringkat)
    if kategori == 'Preskripsi Troli Ubat':
        # Susun dalam 4 lajur x 2 baris supaya kemas
        cols_troli1 = st.columns(4)
        cols_troli2 = st.columns(4)
        semua_lajur = cols_troli1 + cols_troli2
        
        for i, tahap in enumerate(tahap_troli):
            kunci = f"masa_{tahap.replace(' ', '_')}"
            with semua_lajur[i]:
                st.write(f"**{i+1}. {tahap}**")
                st.button(f"🕒 Set {tahap}", on_click=set_masa_live, args=(kunci,), key=f"btn_{kunci}", use_container_width=True)
                masa_dipilih[tahap] = st.time_input(f"Masa:", value=st.session_state[kunci], key=f"input_{kunci}")
    
    # LOGIK B: JIKA FLOOR STOCK / DD (3 Peringkat)
    else:
        cols_lain = st.columns(3)
        for i, tahap in enumerate(tahap_lain):
            kunci = f"masa_{tahap.replace(' ', '_')}"
            with cols_lain[i]:
                st.write(f"**{i+1}. {tahap}**")
                st.button(f"🕒 Set {tahap}", on_click=set_masa_live, args=(kunci,), key=f"btn_{kunci}", use_container_width=True)
                masa_dipilih[tahap] = st.time_input(f"Masa:", value=st.session_state[kunci], key=f"input_{kunci}")

    st.write("")
    
    # BUTANG SIMPAN
    if st.button("💾 SIMPAN REKOD KE DALAM SISTEM", type="primary", use_container_width=True):
        
        # Pengiraan TAT Keseluruhan (Mula hingga Akhir)
        if kategori == 'Preskripsi Troli Ubat':
            mula_dt = datetime.datetime.combine(tarikh, masa_dipilih['Troli Sampai'])
            tamat_dt = datetime.datetime.combine(tarikh, masa_dipilih['Ambil Bekalan'])
        else:
            mula_dt = datetime.datetime.combine(tarikh, masa_dipilih['Masa Sampai'])
            tamat_dt = datetime.datetime.combine(tarikh, masa_dipilih['Ambil Bekalan'])
            
        # Logik jika shift malam
        if tamat_dt < mula_dt:
            tamat_dt += datetime.timedelta(days=1)
            
        tat_minit = (tamat_dt - mula_dt).total_seconds() / 60
        
        # Bina Baris Data Baru
        data_dict = {
            'Tarikh': [tarikh.strftime("%d-%m-%Y")],
            'Kategori': [kategori],
            'Unit / Wad': [unit],
            'TAT Keseluruhan (Minit)': [round(tat_minit, 1)]
        }
        
        # Masukkan semua masa ke dalam jadual
        for tahap, nilai_masa in masa_dipilih.items():
            data_dict[tahap] = [nilai_masa.strftime("%H:%M")]
            
        rekod_baru = pd.DataFrame(data_dict)
        st.session_state['rekod_data'] = pd.concat([st.session_state['rekod_data'], rekod_baru], ignore_index=True)
        st.success(f"✅ Berjaya! Masa Pusingan (TAT) direkodkan: {round(tat_minit, 1)} minit.")

    # Paparan Jadual
    if not st.session_state['rekod_data'].empty:
        st.write("---")
        st.write("### 📋 Senarai Rekod (Sesi Ini)")
        st.dataframe(st.session_state['rekod_data'], use_container_width=True)
        
        csv = st.session_state['rekod_data'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Muat Turun CSV Rekod", data=csv,
            file_name=f"WIPDASH_{tarikh}.csv", mime="text/csv"
        )

# ------------------------------------------
# TAB 2: DASHBOARD ANALITIK (GRAF)
# ------------------------------------------
with tab2:
    df = st.session_state['rekod_data']
    
    if df.empty:
        st.info("ℹ️ Sila simpan sekurang-kurangnya 1 rekod di Tab 1 untuk melihat graf.")
    else:
        st.subheader("📊 Analitik TAT Keseluruhan Semasa")
        kat_pilihan = st.selectbox("Tapis Mengikut Kategori:", ["Paparkan Semua"] + senarai_kategori)
        
        if kat_pilihan != "Paparkan Semua":
            df_graf = df[df['Kategori'] == kat_pilihan]
        else:
            df_graf = df
            
        if not df_graf.empty:
            avg_tat = round(df_graf['TAT Keseluruhan (Minit)'].mean(), 1)
            
            col_kpi1, col_kpi2 = st.columns(2)
            col_kpi1.metric("⏱️ Purata TAT Keseluruhan", f"{avg_tat} Minit")
            col_kpi2.metric("📦 Jumlah Pembekalan Disiapkan", f"{len(df_graf)} Unit")
            
            fig = px.bar(
                df_graf, x='Unit / Wad', y='TAT Keseluruhan (Minit)', 
                color='TAT Keseluruhan (Minit)', title=f"Prestasi: {kat_pilihan}",
                color_continuous_scale='RdYlGn_r', text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Tiada data untuk kategori yang dipilih.")