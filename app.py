import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import uuid

# Set Layout supaya responsif untuk telefon/tablet
st.set_page_config(page_title="Sistem WIPDASH", layout="wide")

# ==========================================
# 1. KAWALAN KESELAMATAN (PIN)
# ==========================================
if 'log_masuk' not in st.session_state: st.session_state['log_masuk'] = False

if not st.session_state['log_masuk']:
    st.title("🔒 Kawalan Keselamatan WIPDASH")
    if st.text_input("Masukkan PIN:", type="password") == "7788":
        st.session_state['log_masuk'] = True
        st.rerun()
    st.stop()

# ==========================================
# 2. INISIALISASI DATABASE & NAVIGASI
# ==========================================
if 'tiket_aktif' not in st.session_state: st.session_state['tiket_aktif'] = {} 
if 'tiket_siap' not in st.session_state: st.session_state['tiket_siap'] = {} 
if 'rekod_selesai' not in st.session_state: st.session_state['rekod_selesai'] = pd.DataFrame() 

# ==========================================
# FUNGSI POP-UP (MODAL)
# ==========================================
@st.dialog("Sahkan Staf Pelaksana")
def dialog_masuk_nama(id_tiket, tahap_kiri):
    st.write(f"Sila masukkan nama untuk rekod **{tahap_kiri}**:")
    nama_in = st.text_input("Nama Anda:", key=f"dialog_in_{id_tiket}_{tahap_kiri}")
    if st.button("Mula Masa", type="primary"):
        if nama_in:
            st.session_state['tiket_aktif'][id_tiket]['Masa'][tahap_kiri] = datetime.datetime.now().strftime("%H:%M")
            if "Saring" in tahap_kiri: st.session_state['tiket_aktif'][id_tiket]['Pelaksana Saringan'] = nama_in
            elif "Fill" in tahap_kiri: st.session_state['tiket_aktif'][id_tiket]['Pelaksana Filling'] = nama_in
            elif "Semak" in tahap_kiri: st.session_state['tiket_aktif'][id_tiket]['Pelaksana Semakan'] = nama_in
            st.rerun()
        else: st.error("Masukkan nama!")

# ==========================================
# 3. ANTARAMUKA NAVIGASI
# ==========================================
st.sidebar.title("Navigasi WIPDASH")
page = st.sidebar.radio("Pilih Modul:", ["Laman Utama", "1. Pendaftaran", "2. Farmasi WIP", "3. Kaunter Serahan", "4. Dashboard", "5. BCP Manual"])

if page == 'Laman Utama':
    st.title("Selamat Datang ke WIPDASH")
    st.info("Pilih modul di menu kiri.")
    if st.button("Log Keluar"): 
        st.session_state['log_masuk'] = False
        st.rerun()

# ---------------------------------------------------------
# LOGIK PENDAFTARAN (DENGAN PENCEGAHAN DUPLIKAT)
# ---------------------------------------------------------
elif page == '1. Pendaftaran':
    st.subheader("Daftar Penerimaan Wad")
    with st.form("daftar_tiket", clear_on_submit=True):
        wad = st.selectbox("Wad:", ['Kenanga 2A', 'Kenanga 2B', 'Kenanga 1A', 'Unit Kecemasan'])
        peng = st.text_input("Nama Penghantar:")
        kat = st.multiselect("Kategori:", ['Preskripsi Troli Ubat', 'Floor Stock', 'Dadah Berbahaya (DD)'])
        submitted = st.form_submit_button("🚀 BUKA TIKET")
        
        if submitted:
            if not peng or not kat: st.error("Lengkapkan maklumat!")
            else:
                for k in kat:
                    id_unik = str(uuid.uuid4())[:8]
                    # Simpan ID unik untuk mengelakkan duplikasi
                    st.session_state['tiket_aktif'][id_unik] = {
                        'Tarikh': datetime.date.today().strftime("%d-%m-%Y"),
                        'Wad': wad, 'Kategori': k, 'Nama Penghantar': peng,
                        'Masa': {'Troli Sampai' if k=='Preskripsi Troli Ubat' else 'Masa Sampai': datetime.datetime.now().strftime("%H:%M")}
                    }
                st.success("Tiket Berjaya Dibuka!")

# ---------------------------------------------------------
# LOGIK FARMASI WIP (INTERAKTIF & LIVE SYNC)
# ---------------------------------------------------------
elif page == '2. Farmasi WIP':
    for id_t, data_t in st.session_state['tiket_aktif'].items():
        with st.expander(f"📌 {data_t['Wad']} - {data_t['Kategori']} (ID: {id_t})"):
            # Proses Butang Punch
            tahap = ['Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap'] if data_t['Kategori'] == 'Preskripsi Troli Ubat' else ['Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap']
            for t in tahap:
                if t not in data_t['Masa']:
                    if st.button(f"Punch {t}", key=f"btn_{id_t}_{t}"):
                        if "Mula" in t: dialog_masuk_nama(id_t, t)
                        else: 
                            data_t['Masa'][t] = datetime.datetime.now().strftime("%H:%M")
                            st.rerun()
            
            # Butang Hantar ke Kaunter
            if st.button("📦 HANTAR KE KAUNTER", key=f"hantar_{id_t}"):
                st.session_state['tiket_siap'][id_t] = data_t
                del st.session_state['tiket_aktif'][id_t]
                st.rerun()

# ---------------------------------------------------------
# (Tiga tab lain seperti kod sebelum ini...)
# ---------------------------------------------------------
