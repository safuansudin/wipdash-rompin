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
# 2. INISIALISASI DATABASE & NAVIGASI
# ==========================================
if 'tiket_aktif' not in st.session_state:
    st.session_state['tiket_aktif'] = {} 
if 'tiket_siap' not in st.session_state:
    st.session_state['tiket_siap'] = {} 
if 'rekod_selesai' not in st.session_state:
    st.session_state['rekod_selesai'] = pd.DataFrame() 

# Sistem Navigasi Muka Surat
if 'page' not in st.session_state:
    st.session_state['page'] = 'Laman Utama'

def tukar_muka(nama_muka):
    st.session_state['page'] = nama_muka

def dapatkan_waktu_malaysia():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).time()

def dapatkan_tarikh_malaysia():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()

def kira_beza_minit(masa_mula, masa_akhir):
    try:
        mula_dt = datetime.datetime.strptime(masa_mula, "%H:%M")
        akhir_dt = datetime.datetime.strptime(masa_akhir, "%H:%M")
        if akhir_dt < mula_dt:
            akhir_dt += datetime.timedelta(days=1)
        return round((akhir_dt - mula_dt).total_seconds() / 60, 1)
    except:
        return 0.0

tahap_farmasi_troli = ['Troli Sampai', 'Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap']
tahap_farmasi_lain = ['Masa Sampai', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap']

senarai_unit = ['Kenanga 2A', 'Kenanga 2B', 'Kenanga 1A', 'Unit Kecemasan & Trauma', 'Klinik Pakar', 'Unit Hemodialisis']
senarai_kategori = ['Preskripsi Troli Ubat', 'Floor Stock', 'Dadah Berbahaya (DD) / Psikotropik']

# ==========================================
# 3. KEPALA (HEADER) SISTEM
# ==========================================
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🏥 Sistem WIPDASH - Hospital Rompin")
with col_logout:
    st.write("")
    if st.button("Log Keluar"):
        st.session_state['log_masuk'] = False
        st.rerun()
st.markdown("---")

# ==========================================
# 4. ENJIN NAVIGASI MUKA SURAT
# ==========================================

# ---------------------------------------------------------
# MUKA SURAT 0: LAMAN UTAMA (MENU KAD INTERAKTIF)
# ---------------------------------------------------------
if st.session_state['page'] == 'Laman Utama':
    st.subheader("Sila pilih modul operasi di bawah:")
    st.write("")
    
    # CSS Custom untuk Kad agar nampak seperti Rujukan Gambar
    st.markdown("""
    <style>
    .kad-menu {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .kad-menu h2 { font-size: 50px; margin-bottom: 0; }
    .kad-menu h4 { color: white; margin-top: 10px; margin-bottom: 5px; font-weight: bold; }
    .kad-menu p { font-size: 14px; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)
    
    # Baris Pertama (3 Kad)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="kad-menu" style="background-color: #EF476F;"><h2>🆕</h2><h4>Pendaftaran Wad</h4><p>Wad daftar masuk bekalan</p></div>', unsafe_allow_html=True)
        st.button("MASUK MODUL ➔", key="btn_m1", use_container_width=True, on_click=tukar_muka, args=("1. Pendaftaran",))

    with col2:
        jumlah_wip = len(st.session_state['tiket_aktif'])
        st.markdown(f'<div class="kad-menu" style="background-color: #118AB2;"><h2>⏳</h2><h4>Farmasi (WIP)</h4><p>{jumlah_wip} tiket sedang berjalan</p></div>', unsafe_allow_html=True)
        st.button("MASUK MODUL ➔", key="btn_m2", use_container_width=True, on_click=tukar_muka, args=("2. Farmasi WIP",))

    with col3:
        jumlah_siap = len(st.session_state['tiket_siap'])
        st.markdown(f'<div class="kad-menu" style="background-color: #06D6A0;"><h2>📦</h2><h4>Kaunter Serahan</h4><p>{jumlah_siap} wad sedia diambil</p></div>', unsafe_allow_html=True)
        st.button("MASUK MODUL ➔", key="btn_m3", use_container_width=True, on_click=tukar_muka, args=("3. Kaunter Serahan",))

    st.write("")
    
    # Baris Kedua (2 Kad)
    col4, col5 = st.columns([1, 1])
    with col4:
        st.markdown('<div class="kad-menu" style="background-color: #FFD166;"><h2 style="color:black;">📊</h2><h4 style="color:black;">Dashboard Analitik</h4><p style="color:black;">Pencapaian KPI & Laporan</p></div>', unsafe_allow_html=True)
        st.button("MASUK MODUL ➔", key="btn_m4", use_container_width=True, on_click=tukar_muka, args=("4. Dashboard",))
        
    with col5:
        st.markdown('<div class="kad-menu" style="background-color: #073B4C;"><h2>⚠️</h2><h4>Pelan BCP</h4><p>Kemasukan data manual log</p></div>', unsafe_allow_html=True)
        st.button("MASUK MODUL ➔", key="btn_m5", use_container_width=True, on_click=tukar_muka, args=("5. BCP Manual",))


# ---------------------------------------------------------
# MUKA SURAT 1: PENDAFTARAN WAD
# ---------------------------------------------------------
elif st.session_state['page'] == '1. Pendaftaran':
    st.button("🔙 Kembali ke Laman Utama", on_click=tukar_muka, args=("Laman Utama",))
    st.markdown("---")
    
    st.subheader("Daftar Penerimaan Wad (Sistem Live)")
    st.caption("Jururawat / PPK: Sila isikan maklumat di bawah dan klik butang untuk mulakan masa.")
    
    col1, col2 = st.columns(2)
    with col1:
        wad_baru = st.selectbox("🏥 Pilih Unit / Wad Anda", senarai_unit, key="wad_live")
        nama_penghantar = st.text_input("👩‍⚕️ Nama Penghantar (Wad):", placeholder="Contoh: SN Aminah", key="penghantar_live")
    with col2:
        kat_baru = st.multiselect("📂 Pilih Kategori Dibawa", senarai_kategori, default=['Preskripsi Troli Ubat'], key="kat_live")
        
    if st.button("🚀 BUKA TIKET & MULAKAN MASA PENGIRAAN", type="primary", use_container_width=True):
        if not nama_penghantar or not kat_baru:
            st.error("⚠️ Sila lengkapkan Nama Penghantar dan Kategori.")
        else:
            for kat in kat_baru:
                id_unik = str(uuid.uuid4())[:8] 
                tahap_mula = 'Troli Sampai' if kat == 'Preskripsi Troli Ubat' else 'Masa Sampai'
                st.session_state['tiket_aktif'][id_unik] = {
                    'Tarikh': dapatkan_tarikh_malaysia().strftime("%d-%m-%Y"),
                    'Wad': wad_baru,
                    'Kategori': kat,
                    'Nama Penghantar': nama_penghantar,
                    'Masa': {tahap_mula: dapatkan_waktu_malaysia().strftime("%H:%M")}
                }
            st.success(f"✅ Tiket dibuka! Sila maklumkan kepada Farmasi.")


# ---------------------------------------------------------
# MUKA SURAT 2: FARMASI (WIP)
# ---------------------------------------------------------
elif st.session_state['page'] == '2. Farmasi WIP':
    st.button("🔙 Kembali ke Laman Utama", on_click=tukar_muka, args=("Laman Utama",))
    st.markdown("---")
    
    st.subheader("Kerja Farmasi Yang Belum Selesai (WIP)")
    
    if not st.session_state['tiket_aktif']:
        st.info("Tiada kerja tertunggak di Farmasi buat masa ini.")
    else:
        senarai_wad_aktif = list(set([data['Wad'] for data in st.session_state['tiket_aktif'].values()]))
        carian_wad = st.multiselect("🔍 Tapis Mengikut Wad:", senarai_wad_aktif)
        
        for id_tiket, data_tiket in list(st.session_state['tiket_aktif'].items()):
            wad = data_tiket['Wad']
            kategori = data_tiket['Kategori']
            
            if carian_wad and wad not in carian_wad:
                continue
                
            tahap_mula = 'Troli Sampai' if kategori == 'Preskripsi Troli Ubat' else 'Masa Sampai'
            status_masa = "⏳ Masa belum bermula"
            if tahap_mula in data_tiket['Masa']:
                minit_menunggu = kira_beza_minit(data_tiket['Masa'][tahap_mula], dapatkan_waktu_malaysia().strftime("%H:%M"))
                status_masa = f"⏱️ Menunggu: {minit_menunggu} minit"

            with st.expander(f"📌 {wad} - {kategori} | {status_masa}", expanded=True):
                senarai_tahap = tahap_farmasi_troli if kategori == 'Preskripsi Troli Ubat' else tahap_farmasi_lain
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
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    saring_val = st.text_input("👨‍⚕️ Pelaksana Saringan:", key=f"pel_s_{id_tiket}") if kategori == 'Preskripsi Troli Ubat' else "N/A"
                with col_p2:
                    fill_val = st.text_input("👨‍⚕️ Pelaksana Filling:", key=f"pel_f_{id_tiket}")
                with col_p3:
                    semak_val = st.text_input("👨‍⚕️ Pelaksana Semakan:", key=f"pel_sm_{id_tiket}")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    pemanggil_val = st.text_input("📞 Pemanggil (Farmasi):", key=f"pemanggil_{id_tiket}")
                with col_c2:
                    penerima_val = st.text_input("👩‍⚕️ Penerima (Wad):", key=f"penerima_{id_tiket}")
                    tak_jawab_val = st.checkbox("⚠️ Panggilan Tidak Berjawab", key=f"tak_jawab_{id_tiket}")
                with col_c3:
                    waktu_call_val = st.time_input("⏰ Waktu Call:", value=dapatkan_waktu_malaysia(), key=f"waktu_call_{id_tiket}")
                
                catatan_val = st.text_area("Catatan Kelewatan:", key=f"catatan_{id_tiket}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"📦 HANTAR KE KAUNTER SERAHAN", key=f"hantar_{id_tiket}", type="primary", use_container_width=True):
                        data_tiket['Pelaksana Saringan'] = saring_val
                        data_tiket['Pelaksana Filling'] = fill_val
                        data_tiket['Pelaksana Semakan'] = semak_val
                        data_tiket['Pemanggil (Farmasi)'] = pemanggil_val
                        data_tiket['Penerima Panggilan (Wad)'] = "TIDAK BERJAWAB" if tak_jawab_val else penerima_val
                        data_tiket['Waktu Dihubungi'] = waktu_call_val.strftime("%H:%M") if waktu_call_val else "-"
                        data_tiket['Catatan / Sebab Lewat'] = catatan_val
                        
                        st.session_state['tiket_siap'][id_tiket] = data_tiket
                        del st.session_state['tiket_aktif'][id_tiket]
                        st.success("Bekalan siap dan dihantar ke Kaunter Serahan!")
                        st.rerun()
                with col_btn2:
                    if st.button(f"🗑️ BATAL TIKET", key=f"batal_{id_tiket}", use_container_width=True):
                        del st.session_state['tiket_aktif'][id_tiket]
                        st.rerun()


# ---------------------------------------------------------
# MUKA SURAT 3: KAUNTER SERAHAN (WAD AMBIL)
# ---------------------------------------------------------
elif st.session_state['page'] == '3. Kaunter Serahan':
    st.button("🔙 Kembali ke Laman Utama", on_click=tukar_muka, args=("Laman Utama",))
    st.markdown("---")
    
    st.subheader("📦 Kaunter Serahan (Sedia Untuk Diambil)")
    
    if not st.session_state['tiket_siap']:
        st.info("Tiada bekalan yang sedang menunggu untuk diambil oleh wad.")
    else:
        wad_siap = {}
        for id_t, data_t in st.session_state['tiket_siap'].items():
            wad = data_t['Wad']
            if wad not in wad_siap:
                wad_siap[wad] = []
            wad_siap[wad].append((id_t, data_t))
            
        for wad, senarai_tiket in wad_siap.items():
            kategori_terlibat = [t[1]['Kategori'] for t in senarai_tiket]
            kat_str = ", ".join(kategori_terlibat)
            
            with st.expander(f"🟢 {wad} - Sedia Diambil ({kat_str})", expanded=True):
                st.write(f"**Terdapat {len(senarai_tiket)} bekalan siap untuk wad ini.**")
                
                nama_pengambil = st.text_input(f"👩‍⚕️ Nama Staf Wad Yang Menuntut:", placeholder="Contoh: SN Aminah", key=f"pengambil_{wad}")
                
                if st.button(f"✅ AMBIL SEMUA BEKALAN {wad.upper()} & TUTUP TIKET", type="primary", key=f"ambil_{wad}"):
                    if not nama_pengambil:
                        st.error("Sila masukkan nama pengambil sebelum menekan butang.")
                    else:
                        masa_ambil_sekarang = dapatkan_waktu_malaysia().strftime("%H:%M")
                        
                        for id_t, data_t in senarai_tiket:
                            kat = data_t['Kategori']
                            tahap_mula = 'Troli Sampai' if kat == 'Preskripsi Troli Ubat' else 'Masa Sampai'
                            data_t['Masa']['Ambil Bekalan'] = masa_ambil_sekarang
                            
                            tat_minit = kira_beza_minit(data_t['Masa'].get(tahap_mula, "00:00"), masa_ambil_sekarang)
                            status_kpi = "Patuh KPI" if (kat != 'Preskripsi Troli Ubat' or tat_minit <= 240) else "Gagal KPI"
                            
                            rekod_baru = {
                                'Tarikh': data_t['Tarikh'], 'Mod Rekod': 'Sistem Live', 'Sebab BCP': '-',
                                'Kategori': kat, 'Unit / Wad': wad, 'Nama Penghantar (Wad)': data_t.get('Nama Penghantar', '-'),
                                'Nama Pengambil (Wad)': nama_pengambil,
                                'Pelaksana Saringan': data_t['Pelaksana Saringan'], 'Pelaksana Filling': data_t['Pelaksana Filling'], 'Pelaksana Semakan': data_t['Pelaksana Semakan'],
                                'Pemanggil (Farmasi)': data_t['Pemanggil (Farmasi)'], 'Penerima Panggilan (Wad)': data_t['Penerima Panggilan (Wad)'],
                                'Waktu Dihubungi': data_t['Waktu Dihubungi'], 'Catatan / Sebab Lewat': data_t['Catatan / Sebab Lewat'],
                                'TAT Keseluruhan (Minit)': tat_minit, 'Status KPI': status_kpi
                            }
                            
                            semua_tahap = tahap_farmasi_troli + ['Ambil Bekalan'] if kat == 'Preskripsi Troli Ubat' else tahap_farmasi_lain + ['Ambil Bekalan']
                            for t in semua_tahap:
                                rekod_baru[t] = data_t['Masa'].get(t, "Tidak Direkod")
                                
                            st.session_state['rekod_selesai'] = pd.concat([st.session_state['rekod_selesai'], pd.DataFrame([rekod_baru])], ignore_index=True)
                            del st.session_state['tiket_siap'][id_t]
                            
                        st.success(f"Bekalan diserahkan kepada {nama_pengambil}. Tiket ditutup!")
                        st.rerun()


# ---------------------------------------------------------
# MUKA SURAT 4: DASHBOARD ANALITIK
# ---------------------------------------------------------
elif st.session_state['page'] == '4. Dashboard':
    st.button("🔙 Kembali ke Laman Utama", on_click=tukar_muka, args=("Laman Utama",))
    st.markdown("---")
    
    df = st.session_state['rekod_selesai']
    if df.empty:
        st.info("Belum ada tiket disiapkan.")
    else:
        st.subheader("📊 Analitik Pencapaian & Dashboard Eksekutif")
        kat_pilihan = st.selectbox("Tapis Laporan:", ["Paparkan Semua"] + senarai_kategori)
        df_graf = df[df['Kategori'] == kat_pilihan] if kat_pilihan != "Paparkan Semua" else df
            
        if not df_graf.empty:
            avg_tat = round(df_graf['TAT Keseluruhan (Minit)'].mean(), 1)
            jumlah_selesai = len(df_graf)
            jumlah_patuh = len(df_graf[df_graf['Status KPI'] == 'Patuh KPI'])
            peratus_kpi = round((jumlah_patuh / jumlah_selesai) * 100, 1) if jumlah_selesai > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("⏱️ Purata TAT", f"{avg_tat} Minit")
            c2.metric("📦 Jumlah Selesai", f"{jumlah_selesai} Tiket")
            c3.metric("📈 Pencapaian KPI", f"{peratus_kpi}%")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig1 = px.bar(df_graf, x='Unit / Wad', y='TAT Keseluruhan (Minit)', color='Status KPI', title="Prestasi Masa Pusingan (TAT)", color_discrete_map={'Patuh KPI': 'green', 'Gagal KPI': 'red'})
                st.plotly_chart(fig1, use_container_width=True)
            with col_g2:
                df_catatan = df_graf[df_graf['Catatan / Sebab Lewat'].str.strip() != ""]
                if not df_catatan.empty:
                    fig2 = px.pie(df_catatan, names='Catatan / Sebab Lewat', title="Analisis Punca Kelewatan", hole=0.3)
                    st.plotly_chart(fig2, use_container_width=True)
                    
        st.write("### 📋 Jadual Rekod Penuh")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Muat Turun CSV", data=df.to_csv(index=False).encode('utf-8'), file_name=f"WIPDASH_{dapatkan_tarikh_malaysia()}.csv", mime="text/csv")


# ---------------------------------------------------------
# MUKA SURAT 5: BCP (KEMASUKAN MANUAL)
# ---------------------------------------------------------
elif st.session_state['page'] == '5. BCP Manual':
    st.button("🔙 Kembali ke Laman Utama", on_click=tukar_muka, args=("Laman Utama",))
    st.markdown("---")
    
    st.subheader("⚠️ BCP (Kemasukan Manual)")
    with st.form("form_bcp", clear_on_submit=True):
        col_bcp1, col_bcp2 = st.columns(2)
        with col_bcp1:
            tarikh_bcp = st.date_input("Tarikh Rekod:", dapatkan_tarikh_malaysia())
            sebab_bcp = st.selectbox("Sebab BCP:", ["Ketiadaan Capaian Internet", "Sistem / Server Tergendala", "Kerosakan Komputer", "Lain-lain"])
        with col_bcp2:
            wad_bcp = st.selectbox("Wad:", senarai_unit)
            kat_bcp = st.selectbox("Kategori:", senarai_kategori)
            
        masa_bcp = {}
        senarai_t_bcp = ['Troli Sampai', 'Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap', 'Ambil Bekalan'] if kat_bcp == 'Preskripsi Troli Ubat' else ['Masa Sampai', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap', 'Ambil Bekalan']
        
        cols_m = st.columns(4)
        for i, t in enumerate(senarai_t_bcp):
            with cols_m[i % 4]:
                masa_bcp[t] = st.time_input(t, value=datetime.time(0, 0), key=f"mb_{t}")
                
        c_ak1, c_ak2, c_ak3 = st.columns(3)
        with c_ak1:
            pengirim_bcp = st.text_input("Pengirim (Wad):")
            pelaksana_s = st.text_input("Pelaksana Saring:") if kat_bcp == 'Preskripsi Troli Ubat' else "N/A"
        with c_ak2:
            pelaksana_f = st.text_input("Pelaksana Fill:")
            pelaksana_sm = st.text_input("Pelaksana Semak:")
        with c_ak3:
            pengambil_bcp = st.text_input("Pengambil (Wad):")
            catatan_bcp = st.text_input("Catatan:")
            
        if st.form_submit_button("💾 SIMPAN MANUAL", type="primary"):
            tahap_mula_bcp = 'Troli Sampai' if kat_bcp == 'Preskripsi Troli Ubat' else 'Masa Sampai'
            tat_bcp = kira_beza_minit(masa_bcp[tahap_mula_bcp].strftime("%H:%M"), masa_bcp['Ambil Bekalan'].strftime("%H:%M"))
            
            rekod_baru_bcp = {
                'Tarikh': tarikh_bcp.strftime("%d-%m-%Y"), 'Mod Rekod': 'Manual (BCP)', 'Sebab BCP': sebab_bcp,
                'Kategori': kat_bcp, 'Unit / Wad': wad_bcp, 'Nama Penghantar (Wad)': pengirim_bcp, 'Nama Pengambil (Wad)': pengambil_bcp,
                'Pelaksana Saringan': pelaksana_s, 'Pelaksana Filling': pelaksana_f, 'Pelaksana Semakan': pelaksana_sm,
                'Catatan / Sebab Lewat': catatan_bcp, 'TAT Keseluruhan (Minit)': tat_bcp, 'Status KPI': "Patuh KPI" if (kat_bcp != 'Preskripsi Troli Ubat' or tat_bcp <= 240) else "Gagal KPI"
            }
            for t in senarai_t_bcp:
                rekod_baru_bcp[t] = masa_bcp[t].strftime("%H:%M")
                
            st.session_state['rekod_selesai'] = pd.concat([st.session_state['rekod_selesai'], pd.DataFrame([rekod_baru_bcp])], ignore_index=True)
            st.success("Rekod manual dimasukkan!")
