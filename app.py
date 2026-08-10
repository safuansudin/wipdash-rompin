import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import uuid

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
            st.rerun()
        else:
            st.error("❌ PIN Salah. Sila cuba lagi.")
    st.stop()

# ==========================================
# 2. INISIALISASI DATABASE & FUNGSI BANTUAN
# ==========================================
if 'tiket_aktif' not in st.session_state:
    st.session_state['tiket_aktif'] = {}

if 'rekod_selesai' not in st.session_state:
    st.session_state['rekod_selesai'] = pd.DataFrame()

def dapatkan_waktu_malaysia():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).time()

def dapatkan_tarikh_malaysia():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()

def kira_beza_minit(masa_mula, masa_akhir):
    mula_dt = datetime.datetime.strptime(masa_mula, "%H:%M")
    akhir_dt = datetime.datetime.strptime(masa_akhir, "%H:%M")
    if akhir_dt < mula_dt:
        akhir_dt += datetime.timedelta(days=1)
    return round((akhir_dt - mula_dt).total_seconds() / 60, 1)

tahap_troli = ['Troli Sampai', 'Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap', 'Ambil Bekalan']
tahap_lain = ['Masa Sampai', 'Bekalan Siap', 'Ambil Bekalan']

# ==========================================
# 3. ANTARAMUKA UTAMA
# ==========================================
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🏥 Sistem WIPDASH - Hospital Rompin (V13)")
with col_logout:
    st.write("")
    if st.button("Log Keluar"):
        st.session_state['log_masuk'] = False
        st.rerun()

senarai_unit = ['Kenanga 2A', 'Kenanga 2B', 'Kenanga 1A', 'Unit Kecemasan & Trauma', 'Klinik Pakar', 'Unit Hemodialisis']
senarai_kategori = ['Preskripsi Troli Ubat', 'Floor Stock', 'Dadah Berbahaya (DD) / Psikotropik']

tab1, tab2, tab3 = st.tabs(["🆕 1. Buka Tiket Baru", "⏳ 2. Kerja Sedang Berjalan (WIP)", "📊 3. Dashboard Analitik"])

# ------------------------------------------
# TAB 1: BUKA TIKET BARU
# ------------------------------------------
with tab1:
    st.subheader("Daftar Penerimaan Baru")
    st.caption("Pilih wad dan kategori, kemudian klik Buka Tiket.")
    
    col1, col2 = st.columns(2)
    with col1:
        wad_baru = st.selectbox("🏥 Pilih Unit / Wad", senarai_unit)
    with col2:
        kat_baru = st.selectbox("📂 Pilih Kategori Pembekalan", senarai_kategori)
        
    if st.button("➕ BUKA TIKET BARU", type="primary"):
        id_unik = str(uuid.uuid4())[:8] 
        st.session_state['tiket_aktif'][id_unik] = {
            'Tarikh': dapatkan_tarikh_malaysia().strftime("%d-%m-%Y"),
            'Wad': wad_baru,
            'Kategori': kat_baru,
            'Masa': {}
        }
        st.success(f"✅ Tiket {wad_baru} ({kat_baru}) berjaya dibuka! Sila ke Tab 2.")

# ------------------------------------------
# TAB 2: KERJA SEDANG BERJALAN (WIP)
# ------------------------------------------
with tab2:
    st.subheader("Senarai Kerja Yang Belum Selesai (WIP)")
    
    if not st.session_state['tiket_aktif']:
        st.info("Bagus! Tiada kerja yang tertunggak buat masa ini.")
    else:
        for id_tiket, data_tiket in list(st.session_state['tiket_aktif'].items()):
            wad = data_tiket['Wad']
            kategori = data_tiket['Kategori']
            
            with st.expander(f"📌 {wad} - {kategori} (ID: {id_tiket})", expanded=True):
                senarai_tahap = tahap_troli if kategori == 'Preskripsi Troli Ubat' else tahap_lain
                
                cols = st.columns(len(senarai_tahap) // 2 if len(senarai_tahap) > 3 else 3)
                
                for i, tahap in enumerate(senarai_tahap):
                    col_index = i % len(cols)
                    with cols[col_index]:
                        if tahap in data_tiket['Masa']:
                            st.success(f"✅ {tahap}\n{data_tiket['Masa'][tahap]}")
                        else:
                            st.write(f"**{tahap}**")
                            if st.button(f"🕒 Punch", key=f"btn_{id_tiket}_{tahap}", use_container_width=True):
                                st.session_state['tiket_aktif'][id_tiket]['Masa'][tahap] = dapatkan_waktu_malaysia().strftime("%H:%M")
                                st.rerun() 
                
                st.markdown("---")
                st.markdown("#### 👤 Jejak Akauntabiliti Kakitangan & Wad")
                
                col_nama1, col_nama2 = st.columns(2)
                with col_nama1:
                    st.text_input("👨‍⚕️ Nama Staf Farmasi Pelaksana:", placeholder="Contoh: Ali / Siti", key=f"pelaksana_{id_tiket}")
                with col_nama2:
                    st.text_input("📞 Nama Staf Farmasi Pemanggil:", placeholder="Contoh: Chong", key=f"pemanggil_{id_tiket}")
                    
                col_nama3, col_nama4 = st.columns(2)
                with col_nama3:
                    st.text_input("👩‍⚕️ Nama Staf Wad Dihubungi (Penerima):", placeholder="Contoh: SN Aminah", key=f"penerima_{id_tiket}")
                    st.checkbox("⚠️ Panggilan Tidak Berjawab (Wad tidak angkat telefon)", key=f"tak_jawab_{id_tiket}")
                with col_nama4:
                    st.time_input("⏰ Waktu Panggilan Dibuat:", value=dapatkan_waktu_malaysia(), key=f"waktu_call_{id_tiket}")
                
                st.markdown("---")
                st.markdown("#### 📝 Catatan Tambahan & Piagam Pelanggan")
                
                # Sistem Penggera Automatik (Auto-Warning)
                if kategori == 'Preskripsi Troli Ubat':
                    st.info("🎯 **Sasaran Piagam Pelanggan:** \n* **Saring:** 2 Jam (120 min) \n* **Filling:** 1 Jam (60 min) \n* **Semak:** 30 Minit \n* **Keseluruhan:** 4 Jam")
                    
                    # Semak Saringan
                    if 'Mula Saring' in data_tiket['Masa'] and 'Tamat Saring' in data_tiket['Masa']:
                        masa_saring = kira_beza_minit(data_tiket['Masa']['Mula Saring'], data_tiket['Masa']['Tamat Saring'])
                        if masa_saring > 120:
                            st.error(f"🚨 **AMARAN:** Proses Saringan mengambil masa {masa_saring} minit (Melebihi target 120 minit!)")
                    
                    # Semak Filling
                    if 'Mula Fill' in data_tiket['Masa'] and 'Tamat Fill' in data_tiket['Masa']:
                        masa_fill = kira_beza_minit(data_tiket['Masa']['Mula Fill'], data_tiket['Masa']['Tamat Fill'])
                        if masa_fill > 60:
                            st.error(f"🚨 **AMARAN:** Proses Filling mengambil masa {masa_fill} minit (Melebihi target 60 minit!)")
                            
                    # Semak Semakan
                    if 'Mula Semak' in data_tiket['Masa'] and 'Bekalan Siap' in data_tiket['Masa']:
                        masa_semak = kira_beza_minit(data_tiket['Masa']['Mula Semak'], data_tiket['Masa']['Bekalan Siap'])
                        if masa_semak > 30:
                            st.error(f"🚨 **AMARAN:** Proses Semakan mengambil masa {masa_semak} minit (Melebihi target 30 minit!)")
                
                st.text_area("Sebab Kelewatan / Catatan (Sila isi jika melepasi Piagam Pelanggan atau terdapat amaran di atas):", placeholder="Contoh: Wad lambat hantar troli / Kekurangan staf", key=f"catatan_{id_tiket}")
                
                st.write("")
                
                if st.button(f"💾 SIAP & SIMPAN KE LAPORAN", key=f"simpan_{id_tiket}", type="primary"):
                    tahap_mula = 'Troli Sampai' if kategori == 'Preskripsi Troli Ubat' else 'Masa Sampai'
                    tahap_akhir = 'Ambil Bekalan'
                    
                    if tahap_mula in data_tiket['Masa'] and tahap_akhir in data_tiket['Masa']:
                        tat_minit = kira_beza_minit(data_tiket['Masa'][tahap_mula], data_tiket['Masa'][tahap_akhir])
                    else:
                        tat_minit = 0.0 
                    
                    panggilan_tak_jawab = st.session_state.get(f"tak_jawab_{id_tiket}", False)
                    penerima_wad = "TIDAK BERJAWAB" if panggilan_tak_jawab else st.session_state.get(f"penerima_{id_tiket}", "")
                    
                    waktu_call_value = st.session_state.get(f"waktu_call_{id_tiket}")
                    waktu_call_str = waktu_call_value.strftime("%H:%M") if waktu_call_value else "Tidak Direkod"

                    rekod_baru = {
                        'Tarikh': data_tiket['Tarikh'], 
                        'Kategori': kategori, 
                        'Unit / Wad': wad, 
                        'Pelaksana (Farmasi)': st.session_state.get(f"pelaksana_{id_tiket}", ""),
                        'Pemanggil (Farmasi)': st.session_state.get(f"pemanggil_{id_tiket}", ""),
                        'Penerima Panggilan (Wad)': penerima_wad,
                        'Waktu Dihubungi': waktu_call_str,
                        'Catatan / Sebab Lewat': st.session_state.get(f"catatan_{id_tiket}", ""),
                        'TAT Keseluruhan (Minit)': tat_minit
                    }
                    for t in senarai_tahap:
                        rekod_baru[t] = data_tiket['Masa'].get(t, "Tidak Direkod")
                        
                    df_baru = pd.DataFrame([rekod_baru])
                    st.session_state['rekod_selesai'] = pd.concat([st.session_state['rekod_selesai'], df_baru], ignore_index=True)
                    
                    del st.session_state['tiket_aktif'][id_tiket]
                    st.success("Rekod berserta catatan kelewatan berjaya disimpan!")
                    st.rerun()

# ------------------------------------------
# TAB 3: DASHBOARD & REKOD SELESAI
# ------------------------------------------
with tab3:
    df = st.session_state['rekod_selesai']
    
    if df.empty:
        st.info("Belum ada tiket yang disiapkan dan disimpan.")
    else:
        st.subheader("📊 Analitik Pencapaian & Sejarah")
        
        kat_pilihan = st.selectbox("Tapis Graf Mengikut Kategori:", ["Paparkan Semua"] + senarai_kategori)
        df_graf = df[df['Kategori'] == kat_pilihan] if kat_pilihan != "Paparkan Semua" else df
            
        if not df_graf.empty:
            avg_tat = round(df_graf['TAT Keseluruhan (Minit)'].mean(), 1)
            col_kpi1, col_kpi2 = st.columns(2)
            col_kpi1.metric("⏱️ Purata TAT Keseluruhan", f"{avg_tat} Minit")
            col_kpi2.metric("📦 Jumlah Pembekalan Selesai", f"{len(df_graf)} Tiket")
            
            fig = px.bar(
                df_graf, x='Unit / Wad', y='TAT Keseluruhan (Minit)', 
                color='TAT Keseluruhan (Minit)', title=f"Prestasi: {kat_pilihan}",
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        st.write("---")
        st.write("### 📋 Jadual Rekod Penuh")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Muat Turun CSV", data=csv, file_name=f"WIPDASH_Laporan_{dapatkan_tarikh_malaysia()}.csv", mime="text/csv")
