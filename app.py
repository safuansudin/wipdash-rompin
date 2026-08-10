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
    try:
        mula_dt = datetime.datetime.strptime(masa_mula, "%H:%M")
        akhir_dt = datetime.datetime.strptime(masa_akhir, "%H:%M")
        if akhir_dt < mula_dt:
            akhir_dt += datetime.timedelta(days=1)
        return round((akhir_dt - mula_dt).total_seconds() / 60, 1)
    except:
        return 0.0

tahap_troli = ['Troli Sampai', 'Mula Saring', 'Tamat Saring', 'Mula Fill', 'Tamat Fill', 'Mula Semak', 'Bekalan Siap', 'Ambil Bekalan']
tahap_lain = ['Masa Sampai', 'Bekalan Siap', 'Ambil Bekalan']

# ==========================================
# 3. ANTARAMUKA UTAMA
# ==========================================
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🏥 Sistem WIPDASH - Hospital Rompin (V18)")
with col_logout:
    st.write("")
    if st.button("Log Keluar"):
        st.session_state['log_masuk'] = False
        st.rerun()

senarai_unit = ['Kenanga 2A', 'Kenanga 2B', 'Kenanga 1A', 'Unit Kecemasan & Trauma', 'Klinik Pakar', 'Unit Hemodialisis']
senarai_kategori = ['Preskripsi Troli Ubat', 'Floor Stock', 'Dadah Berbahaya (DD) / Psikotropik']

tab1, tab2, tab3, tab4 = st.tabs(["🆕 1. Kaunter Wad (Buka Tiket)", "⏳ 2. Kerja Sedang Berjalan", "📊 3. Dashboard Analitik", "⚠️ 4. BCP (Kemasukan Manual)"])

# ------------------------------------------
# TAB 1: BUKA TIKET BARU (KAUNTER WAD)
# ------------------------------------------
with tab1:
    st.subheader("Daftar Penerimaan Wad (Sistem Live)")
    st.caption("Jururawat / PPK: Sila isikan maklumat di bawah dan klik butang untuk mulakan masa.")
    
    col1, col2 = st.columns(2)
    with col1:
        wad_baru = st.selectbox("🏥 Pilih Unit / Wad Anda", senarai_unit, key="wad_live")
        nama_penghantar = st.text_input("👩‍⚕️ Nama Penghantar:", placeholder="Contoh: SN Aminah / PPK Raju", key="penghantar_live")
    with col2:
        kat_baru = st.multiselect("📂 Pilih Kategori Dibawa (Boleh pilih lebih dari 1)", senarai_kategori, default=['Preskripsi Troli Ubat'], key="kat_live")
        
    if st.button("🚀 BUKA TIKET & MULAKAN MASA PENGIRAAN", type="primary", use_container_width=True):
        if not nama_penghantar:
            st.error("⚠️ Sila masukkan Nama Penghantar sebelum menekan butang.")
        elif not kat_baru:
            st.error("⚠️ Sila pilih sekurang-kurangnya satu kategori.")
        else:
            for kat in kat_baru:
                id_unik = str(uuid.uuid4())[:8] 
                tahap_mula = 'Troli Sampai' if kat == 'Preskripsi Troli Ubat' else 'Masa Sampai'
                
                st.session_state['tiket_aktif'][id_unik] = {
                    'Tarikh': dapatkan_tarikh_malaysia().strftime("%d-%m-%Y"),
                    'Wad': wad_baru,
                    'Kategori': kat,
                    'Nama Penghantar': nama_penghantar,
                    'Masa': {
                        tahap_mula: dapatkan_waktu_malaysia().strftime("%H:%M")
                    }
                }
            st.success(f"✅ Tiket dibuka! Sila maklumkan kepada Farmasi.")

# ------------------------------------------
# TAB 2: KERJA SEDANG BERJALAN (WIP)
# ------------------------------------------
with tab2:
    st.subheader("Senarai Kerja Yang Belum Selesai (WIP)")
    
    if not st.session_state['tiket_aktif']:
        st.info("Bagus! Tiada kerja yang tertunggak buat masa ini.")
    else:
        senarai_wad_aktif = list(set([data['Wad'] for data in st.session_state['tiket_aktif'].values()]))
        carian_wad = st.multiselect("🔍 Tapis Mengikut Wad (Biarkan kosong untuk lihat semua):", senarai_wad_aktif)
        st.markdown("---")
        
        for id_tiket, data_tiket in list(st.session_state['tiket_aktif'].items()):
            wad = data_tiket['Wad']
            kategori = data_tiket['Kategori']
            penghantar = data_tiket.get('Nama Penghantar', 'Tidak Direkod')
            
            if carian_wad and wad not in carian_wad:
                continue
                
            tahap_mula = 'Troli Sampai' if kategori == 'Preskripsi Troli Ubat' else 'Masa Sampai'
            if tahap_mula in data_tiket['Masa']:
                minit_menunggu = kira_beza_minit(data_tiket['Masa'][tahap_mula], dapatkan_waktu_malaysia().strftime("%H:%M"))
                status_masa = f"⏱️ Menunggu: {minit_menunggu} minit"
            else:
                status_masa = "⏳ Masa belum bermula"

            tajuk_tiket = f"📌 {wad} - {kategori} | {status_masa} | (Pengirim: {penghantar})"
            
            with st.expander(tajuk_tiket, expanded=True):
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
                st.markdown("#### 👤 Jejak Akauntabiliti")
                
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    st.text_input("👨‍⚕️ Pelaksana:", key=f"pelaksana_{id_tiket}")
                with col_n2:
                    st.text_input("📞 Pemanggil:", key=f"pemanggil_{id_tiket}")
                    
                col_n3, col_n4 = st.columns(2)
                with col_n3:
                    st.text_input("👩‍⚕️ Penerima (Wad):", key=f"penerima_{id_tiket}")
                    st.checkbox("⚠️ Tak Berjawab", key=f"tak_jawab_{id_tiket}")
                with col_n4:
                    st.time_input("⏰ Waktu Call:", value=dapatkan_waktu_malaysia(), key=f"waktu_call_{id_tiket}")
                
                st.text_area("Catatan Kelewatan:", key=f"catatan_{id_tiket}")
                
                col_btn_simpan, col_btn_batal = st.columns(2)
                with col_btn_simpan:
                    if st.button(f"💾 SIAP & SIMPAN (LIVE)", key=f"simpan_{id_tiket}", type="primary", use_container_width=True):
                        tahap_akhir = 'Ambil Bekalan'
                        tat_minit = kira_beza_minit(data_tiket['Masa'].get(tahap_mula, "00:00"), data_tiket['Masa'].get(tahap_akhir, "00:00"))
                        
                        status_kpi = "Patuh KPI" if (kategori != 'Preskripsi Troli Ubat' or tat_minit <= 240) else "Gagal KPI"
                        penerima_wad = "TIDAK BERJAWAB" if st.session_state.get(f"tak_jawab_{id_tiket}") else st.session_state.get(f"penerima_{id_tiket}", "")
                        waktu_call = st.session_state.get(f"waktu_call_{id_tiket}")
                        
                        rekod_baru = {
                            'Tarikh': data_tiket['Tarikh'], 'Mod Rekod': 'Sistem Live', 'Sebab BCP': '-',
                            'Kategori': kategori, 'Unit / Wad': wad, 'Nama Penghantar (Wad)': penghantar,
                            'Pelaksana (Farmasi)': st.session_state.get(f"pelaksana_{id_tiket}", ""),
                            'Pemanggil (Farmasi)': st.session_state.get(f"pemanggil_{id_tiket}", ""),
                            'Penerima Panggilan (Wad)': penerima_wad,
                            'Waktu Dihubungi': waktu_call.strftime("%H:%M") if waktu_call else "Tidak Direkod",
                            'Catatan / Sebab Lewat': st.session_state.get(f"catatan_{id_tiket}", ""),
                            'TAT Keseluruhan (Minit)': tat_minit, 'Status KPI': status_kpi
                        }
                        for t in senarai_tahap:
                            rekod_baru[t] = data_tiket['Masa'].get(t, "Tidak Direkod")
                            
                        st.session_state['rekod_selesai'] = pd.concat([st.session_state['rekod_selesai'], pd.DataFrame([rekod_baru])], ignore_index=True)
                        del st.session_state['tiket_aktif'][id_tiket]
                        st.success("Rekod disimpan!")
                        st.rerun()
                        
                with col_btn_batal:
                    if st.button(f"🗑️ BATAL / PADAM TIKET INI", key=f"batal_{id_tiket}", use_container_width=True):
                        del st.session_state['tiket_aktif'][id_tiket]
                        st.warning("Tiket dibatalkan.")
                        st.rerun()

# ------------------------------------------
# TAB 3: DASHBOARD & REKOD SELESAI
# ------------------------------------------
with tab3:
    df = st.session_state['rekod_selesai']
    
    if df.empty:
        st.info("Belum ada tiket yang disiapkan dan disimpan.")
    else:
        st.subheader("📊 Analitik Pencapaian & Dashboard Eksekutif")
        st.caption("Nota: Anda boleh muat turun gambar graf dengan melalukan *mouse* ke atas graf dan klik ikon kamera (Download plot as a png).")
        
        kat_pilihan = st.selectbox("Tapis Laporan Mengikut Kategori:", ["Paparkan Semua"] + senarai_kategori)
        df_graf = df[df['Kategori'] == kat_pilihan] if kat_pilihan != "Paparkan Semua" else df
            
        if not df_graf.empty:
            avg_tat = round(df_graf['TAT Keseluruhan (Minit)'].mean(), 1)
            jumlah_selesai = len(df_graf)
            jumlah_patuh = len(df_graf[df_graf['Status KPI'] == 'Patuh KPI'])
            peratus_kpi = round((jumlah_patuh / jumlah_selesai) * 100, 1) if jumlah_selesai > 0 else 0
            
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            col_kpi1.metric("⏱️ Purata TAT", f"{avg_tat} Minit")
            col_kpi2.metric("📦 Jumlah Selesai", f"{jumlah_selesai} Tiket")
            col_kpi3.metric("📈 Pencapaian KPI", f"{peratus_kpi}%", f"{jumlah_patuh} patuh dari {jumlah_selesai}")
            
            st.markdown("---")
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                fig1 = px.bar(df_graf, x='Unit / Wad', y='TAT Keseluruhan (Minit)', color='Status KPI', title=f"Prestasi Masa Pusingan (TAT)", color_discrete_map={'Patuh KPI': 'green', 'Gagal KPI': 'red'})
                st.plotly_chart(fig1, use_container_width=True)
                
            with col_graf2:
                df_catatan = df_graf[df_graf['Catatan / Sebab Lewat'].str.strip() != ""]
                if not df_catatan.empty:
                    fig2 = px.pie(df_catatan, names='Catatan / Sebab Lewat', title="Analisis Punca Kelewatan", hole=0.3)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Tiada rekod kelewatan/catatan ditemui.")
            
        st.write("---")
        st.write("### 📋 Jadual Rekod Penuh")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Muat Turun CSV Laporan Lengkap", data=csv, file_name=f"WIPDASH_Laporan_{dapatkan_tarikh_malaysia()}.csv", mime="text/csv")

# ------------------------------------------
# TAB 4: BCP (KEMASUKAN MANUAL)
# ------------------------------------------
with tab4:
    st.subheader("⚠️ Pelan Kesinambungan Perkhidmatan (BCP)")
    st.info("Borang ini Khas untuk kemasukan data (Backlog) daripada Buku Log Kertas sekiranya berlaku gangguan operasi (Downtime).")
    
    with st.form("form_bcp", clear_on_submit=True):
        st.markdown("#### 1. Maklumat Insiden & Wad")
        col_bcp1, col_bcp2 = st.columns(2)
        with col_bcp1:
            tarikh_bcp = st.date_input("📅 Tarikh Rekod (Kertas):", dapatkan_tarikh_malaysia())
            sebab_bcp = st.selectbox("⚡ Sebab Kemasukan Manual (Klausa BCP):", ["Ketiadaan Capaian Internet", "Sistem / Server Tergendala", "Kerosakan Perkakasan Komputer", "Gangguan Bekalan Elektrik", "Lain-lain"])
        with col_bcp2:
            wad_bcp = st.selectbox("🏥 Unit / Wad:", senarai_unit, key="wad_bcp")
            kat_bcp = st.selectbox("📂 Kategori:", senarai_kategori, key="kat_bcp")
            
        st.markdown("#### 2. Jejak Masa (Sila Rujuk Buku Log)")
        masa_bcp = {}
        senarai_tahap_bcp = tahap_troli if kat_bcp == 'Preskripsi Troli Ubat' else tahap_lain
        
        cols_masa_bcp = st.columns(4)
        for i, tahap in enumerate(senarai_tahap_bcp):
            with cols_masa_bcp[i % 4]:
                masa_bcp[tahap] = st.time_input(tahap, value=datetime.time(0, 0), key=f"masa_bcp_{tahap}")
        
        st.markdown("#### 3. Jejak Akauntabiliti")
        col_ak1, col_ak2, col_ak3, col_ak4 = st.columns(4)
        with col_ak1:
            penghantar_bcp = st.text_input("Pengirim Wad:")
        with col_ak2:
            pelaksana_bcp = st.text_input("Pelaksana Farmasi:")
        with col_ak3:
            penerima_bcp = st.text_input("Penerima Wad (Call):")
        with col_ak4:
            catatan_bcp = st.text_input("Catatan Tambahan:")
            
        st.write("")
        simpan_bcp = st.form_submit_button("💾 SIMPAN REKOD MANUAL KE DALAM SISTEM", type="primary", use_container_width=True)
        
        if simpan_bcp:
            tahap_mula_bcp = 'Troli Sampai' if kat_bcp == 'Preskripsi Troli Ubat' else 'Masa Sampai'
            tahap_akhir_bcp = 'Ambil Bekalan'
            
            tat_minit_bcp = kira_beza_minit(masa_bcp[tahap_mula_bcp].strftime("%H:%M"), masa_bcp[tahap_akhir_bcp].strftime("%H:%M"))
            status_kpi_bcp = "Patuh KPI" if (kat_bcp != 'Preskripsi Troli Ubat' or tat_minit_bcp <= 240) else "Gagal KPI"
            
            rekod_baru_bcp = {
                'Tarikh': tarikh_bcp.strftime("%d-%m-%Y"), 'Mod Rekod': 'Kemasukan Manual (BCP)', 'Sebab BCP': sebab_bcp,
                'Kategori': kat_bcp, 'Unit / Wad': wad_bcp, 'Nama Penghantar (Wad)': penghantar_bcp,
                'Pelaksana (Farmasi)': pelaksana_bcp, 'Pemanggil (Farmasi)': '-',
                'Penerima Panggilan (Wad)': penerima_bcp, 'Waktu Dihubungi': '-',
                'Catatan / Sebab Lewat': catatan_bcp, 'TAT Keseluruhan (Minit)': tat_minit_bcp, 'Status KPI': status_kpi_bcp
            }
            
            for t in senarai_tahap_bcp:
                rekod_baru_bcp[t] = masa_bcp[t].strftime("%H:%M")
                
            st.session_state['rekod_selesai'] = pd.concat([st.session_state['rekod_selesai'], pd.DataFrame([rekod_baru_bcp])], ignore_index=True)
            st.success(f"✅ Rekod manual untuk {wad_bcp} (Tat: {tat_minit_bcp} minit) telah berjaya dimasukkan ke dalam Dashboard Utama!")
