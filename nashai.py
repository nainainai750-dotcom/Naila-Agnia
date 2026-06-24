import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. KONFIGURASI HALAMAN & TAMPILAN (UI/CSS)
# ==========================================
st.set_page_config(page_title="Nashai - Belajar Qiro'ah", page_icon="🌟", layout="centered")

st.markdown("""
    <style>
    .title-text { color: #FF6B6B; font-family: 'Comic Sans MS', cursive, sans-serif; text-align: center; }
    .subtitle-text { color: #4ECDC4; text-align: center; font-size: 18px; font-weight: bold; }
    .stButton>button { 
        background-color: #FFE66D; 
        color: #FF6B6B; 
        border-radius: 20px; 
        border: 2px solid #FF6B6B; 
        font-weight: bold; 
        width: 100%;
    }
    .stButton>button:hover { background-color: #FF6B6B; color: #FFE66D; }
    .chat-box { border-radius: 15px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# ==========================================
# 3. HALAMAN LOGIN & PENGATURAN AWAL
# ==========================================
def login_page():
    st.markdown("<h1 class='title-text'>🌟 Ahlan wa Sahlan di Nashai! 🌟</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Ayo belajar membaca teks Bahasa Arab (Maharah Qiro'ah) dengan seru!</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.write("### 📝 Masukkan Data Dirimu Dulu Yuk!")
    username = st.text_input("👤 Nama Panggilan Kamu:")
    api_key = st.text_input("🔑 API Key (Google AI Studio):", type="password")
    
    st.write("### 🎯 Pilih Guru & Materi Belajarmu:")
    ustadz = st.selectbox("👩‍🏫/👨‍🏫 Pilih Pengajar:", ["Ustadz Adam", "Ustadzah Hawa"])
    materi = st.selectbox("📚 Pilih Materi Qiro'ah (Kelas 6 MI):", [
        "1. Al-Madrasah (Sekolah)", 
        "2. Al-Baitun (Rumah)", 
        "3. Usrati (Keluargaku)"
    ])
    
    if st.button("🚀 Mulai Belajar Sekarang!"):
        if username and api_key:
            st.session_state.username = username
            st.session_state.api_key = api_key
            st.session_state.ustadz = ustadz
            st.session_state.materi = materi
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Eits, Nama dan API Key tidak boleh kosong ya! 😉")

# ==========================================
# 4. HALAMAN PERCAKAPAN UTAMA (CHATBOT)
# ==========================================
def chat_page():
    st.sidebar.markdown("### 📌 Info Sesi Belajar")
    st.sidebar.markdown(f"**👤 Siswa:** {st.session_state.username}")
    st.sidebar.markdown(f"**🎙️ Guru:** {st.session_state.ustadz}")
    st.sidebar.markdown(f"**🏫 Materi:** {st.session_state.materi}")
    
    if st.sidebar.button("🚪 Keluar Aplikasi"):
        st.session_state.clear()
        st.rerun()

    st.markdown(f"<h2 class='title-text'>Ruang Belajar Bersama {st.session_state.ustadz} ⛺</h2>", unsafe_allow_html=True)

    try:
        genai.configure(api_key=st.session_state.api_key)
        
        # Ambil daftar model yang tersedia
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        chosen_model = None
        for target in ['models/gemini-1.5-flash', 'models/gemini-2.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in available_models:
                chosen_model = target
                break
        
        if not chosen_model and available_models:
            chosen_model = available_models[0]
            
        model = genai.GenerativeModel(model_name=chosen_model)

        # Inisialisasi instruksi persona
        if st.session_state.chat_session is None:
            system_prompt = f"Kamu adalah {st.session_state.ustadz}, seorang guru Bahasa Arab yang ramah, hangat, dan komunikatif untuk anak-anak kelas 6 MI. Sapa muridmu yang bernama {st.session_state.username}. Gunakan panggilan 'saya/bapak/ibu' atau 'aku' untuk dirimu sendiri. Jangan kaku seperti robot komputer. Fokus materi: Maharah Qiro'ah (Keterampilan Membaca Bahasa Arab) dengan tema {st.session_state.materi}. Berikan teks pendek bahasa Arab berserta harakat, minta anak membacanya, dan bantu menterjemahkannya. Beri pujian yang memotivasi dan gunakan emoji ceria. Jika pengguna mengetik 'exit', 'quit', 'keluar', atau 'selesai', berikan salam perpisahan yang hangat."
            
            initial_history = [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["Wa'alaikumussalam. Baik, saya mengerti. Saya siap menjadi guru yang ramah dan menyenangkan untuk sesi Qiro'ah ini!"]}
            ]
            
            st.session_state.chat_session = model.start_chat(history=initial_history)
            
            greeting = f"Assalamu'alaikum warahmatullahi wabarakatuh, {st.session_state.username}! 👋 Ahlan wa sahlan di Nashai. Saya {st.session_state.ustadz}. Hari ini kita akan seru-seruan belajar membaca (Qiro'ah) tentang {st.session_state.materi}. Sudah siap mulai belajar? 🤩"
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str:
            st.error("⏳ Maaf, kuota API Key kamu sedang penuh/habis. Silakan tunggu beberapa menit atau gunakan API Key dari akun Google yang baru.")
        else:
            st.error(f"Maaf, sepertinya API Key kamu bermasalah. Detail: {e}")
        return

    # Tampilkan chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(f"Ketik pesanmu di sini, {st.session_state.username}...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        if user_input.lower() in ['exit', 'quit', 'keluar', 'selesai']:
            goodbye_msg = f"Alhamdulillah, kelas kita hari ini selesai. Syukran {st.session_state.username} sudah belajar dengan hebat hari ini! Jangan lupa di-muroja'ah (diulang) lagi ya bacaannya. Wassalamu'alaikum! 👋😊"
            with st.chat_message("assistant"):
                st.markdown(goodbye_msg)
            st.session_state.messages.append({"role": "assistant", "content": goodbye_msg})
            st.info("💡 Sesi percakapan dihentikan. Silakan klik tombol **'Keluar Aplikasi'** di menu kiri untuk mereset program.")
        else:
            try:
                # Mengirim pesan ke AI
                response = st.session_state.chat_session.send_message(user_input)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                # Menangkap error 429 Quota Exceeded agar tidak tampil kode merah panjang
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    st.warning("⏳ Waduh, sistem Google sedang membatasi pesan karena kamu sudah mencapai batas limit gratis (Quota Exceeded). Coba tunggu sekitar 1 menit lalu ketik lagi, atau ganti API Key dengan akun baru ya!")
                else:
                    st.error(f"Maaf, terjadi kesalahan saat memproses balasan: {e}")

# ==========================================
# 5. LOGIKA PENGALIHAN HALAMAN
# ==========================================
if not st.session_state.logged_in:
    login_page()
else:
    chat_page()