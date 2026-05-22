import os
import cv2
import numpy as np
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
from PIL import Image
from tensorflow.keras.models import load_model
import streamlit as st

# ---------------- CONFIG ----------------
st.set_page_config(page_title="DeepSentinel | Streamlit OSINT", layout="wide")

# ---------------- PREMIUM WHITE & TEAL DYNAMIC UI ----------------
st.markdown("""
<style>
/* 🌌 High-Contrast Light Matrix Background */
.stApp {
    background: radial-gradient(circle at top right, #f0fdfa, #f8fafc);
    color: #0f172a;
    font-family: 'Inter', system-ui, sans-serif;
}

/* 🧠 Hyper-Glow Teal Title */
.title {
    text-align: center;
    font-size: 64px;
    font-weight: 900;
    background: linear-gradient(90deg, #0d9488, #06b6d4, #0284c7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 10px 30px rgba(6, 182, 212, 0.15);
    margin-bottom: 5px;
    letter-spacing: -2px;
}

.subtitle {
    text-align: center;
    font-size: 14px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.3em;
    margin-bottom: 40px;
    text-transform: uppercase;
}

/* 🪟 Premium Minimalist Cards */
.card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 24px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(13, 148, 136, 0.12);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    border: 1px solid rgba(6, 182, 212, 0.4);
    box-shadow: 0 20px 40px -15px rgba(6, 182, 212, 0.12);
    transform: translateY(-2px);
}

/* 🔘 Dynamic Teal Buttons */
.stButton>button {
    background: linear-gradient(90deg, #0d9488, #06b6d4);
    color: white !important;
    border-radius: 14px;
    border: none;
    padding: 12px 28px;
    font-weight: 700;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
}

.stButton>button:hover {
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
    transform: translateY(-2px);
    filter: brightness(1.1);
}

/* 🧾 Clean Light Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid rgba(13, 148, 136, 0.1);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
}

/* Indicators */
.metric-title {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">DEEP<span style="color:#06b6d4;">SENTINEL</span></p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Streamlit Cyber Intelligence Node</p>', unsafe_allow_html=True)

# ---------------- AI MODEL CORE ENGINE ----------------
@st.cache_resource
def load_deepfake_engine():
    return load_model("deepfake_model_v2.h5", compile=False)

model = load_deepfake_engine()
face_cascade = cv2.CascadeClassifier("haarcascade.xml")

if "history" not in st.session_state:
    st.session_state.history = []

# 🟢 FIXED LOGIC: RGB Space Preprocessing to eliminate Fake False Positives
def preprocess_face(cropped_face_bgr):
    # Convert OpenCV BGR frame patch to Model Training RGB standard
    face_rgb = cv2.cvtColor(cropped_face_bgr, cv2.COLOR_BGR2RGB)
    face_resized = cv2.resize(face_rgb, (128, 128))
    # Explicit float32 scaling matching full-stack requirements
    face_normalized = face_resized.astype("float32") / 255.0
    return np.expand_dims(face_normalized, axis=0)

def evaluate_frame(processed_patch):
    pred = model.predict(processed_patch, verbose=0)[0][0]
    label = "FAKE" if pred > 0.5 else "REAL"
    conf = float(pred if label == "FAKE" else 1 - pred)
    return label, conf

# ---------------- INTERACTION SIDEBAR ----------------
st.sidebar.markdown("<h3 style='color:#0d9488; font-weight:800; margin-bottom:15px;'>TACTICAL INTERFACE</h3>", unsafe_allow_html=True)
mode = st.sidebar.radio("Analysis Spectrum", ["Image Patch", "Video stream", "Live Peripheral (Webcam)"])

# ---------------- STATUS SUMMARY BAR ----------------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='card'><p class='metric-title'>Core Core Architecture</p><p class='metric-value' style='color:#0d9488;'>CNN Engine</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='card'><p class='metric-title'>Mission Profile</p><p class='metric-value' style='color:#06b6d4;'>Active Node</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='card'><p class='metric-title'>Target Input</p><p class='metric-value'>{mode}</p></div>", unsafe_allow_html=True)

# ---------------- MULTI-PANEL SPLIT ----------------
left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🎯 Neural Analysis Terminal")

    if mode == "Image Patch":
        file = st.file_uploader("Inject High-Res Target Image", type=["jpg", "png", "jpeg"])
        if file:
            image = Image.open(file)
            img = np.array(image)
            
            # Keep backup layout clean
            if img.shape[2] == 4:  # Handle RGBA images gracefully
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                
            st.image(image, use_container_width=True)

            if st.button("EXECUTE NEURAL SCAN"):
                # OpenCV operations happen on Gray/BGR tracking scales
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape)==3 else img
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                if len(faces) == 0:
                    st.warning("No face vectors discovered in patch.")
                else:
                    for (x, y, w, h) in faces:
                        face_cropped = img[y:y+h, x:x+w]
                        inp = preprocess_face(face_cropped)
                        label, conf = evaluate_frame(inp)

                        st.session_state.history.append({
                            "Timestamp": pd.Timestamp.now().strftime('%H:%M:%S'),
                            "Type": "Image Scan",
                            "Result": label,
                            "Confidence": f"{conf*100:.1f}%"
                        })

                        # BGR/RGB selection color coordinates
                        border_color = (244, 63, 94) if label == "FAKE" else (16, 185, 129)
                        cv2.rectangle(img, (x, y), (x+w, y+h), border_color, 4)
                        
                        # Add Text labels onto target image preview
                        cv2.putText(img, f"{label} {conf*100:.0f}%", (x, y-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, border_color, 2)

                    st.image(img, caption="Neural Mapping Analytics", use_container_width=True)

    elif mode == "Video stream":
        file = st.file_uploader("Inject Verification Stream (MP4)", type=["mp4"])
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(file.read())
                path = tmp.name

            st.video(path)

            if st.button("RUN STREAM ANALYSIS"):
                cap = cv2.VideoCapture(path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                step = max(1, total_frames // 30)

                confidence_array = []
                verdicts = []
                frame_id = 0
                bar = st.progress(0)

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_id % step == 0:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                        for (x, y, w, h) in faces:
                            face_patch = frame[y:y+h, x:x+w]
                            inp = preprocess_face(face_patch)
                            label, conf = evaluate_frame(inp)
                            confidence_array.append(conf)
                            verdicts.append(label)

                    frame_id += 1
                    bar.progress(min(frame_id / total_frames, 1.0))

                cap.release()
                bar.empty()

                if confidence_array:
                    avg_confidence = sum(confidence_array) / len(confidence_array)
                    # Verdict: Marked compromise if deepfakes are uncovered inside stream frames
                    final_verdict = "FAKE" if verdicts.count("FAKE") > (len(verdicts) * 0.2) else "REAL"

                    st.session_state.history.append({
                        "Timestamp": pd.Timestamp.now().strftime('%H:%M:%S'),
                        "Type": "Stream Engine",
                        "Result": final_verdict,
                        "Confidence": f"{avg_confidence*100:.1f}%"
                    })

                    if final_verdict == "FAKE":
                        st.error(f"🚨 INTEGRITY CRITICAL: Stream evaluated as MANIPULATED ({avg_confidence*100:.1f}%)")
                    else:
                        st.success(f"✅ VETTED AUTHENTIC: Stream evaluated as SECURE ({avg_confidence*100:.1f}%)")
                else:
                    st.warning("Analysis complete: No target biometric traces located.")
            
            try: os.remove(path)
            except: pass

    elif mode == "Live Peripheral (Webcam)":
        run = st.checkbox("Engage Biometric Sensor Hardware")
        frame_window = st.image([])
        cap = cv2.VideoCapture(0)

        while run:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_patch = frame[y:y+h, x:x+w]
                inp = preprocess_face(face_patch)
                label, conf = evaluate_frame(inp)

                # Realtime live console adjustments
                border_color = (94, 63, 244) if label == "FAKE" else (129, 185, 16) # BGR Space mappings
                cv2.rectangle(frame, (x, y), (x+w, y+h), border_color, 3)
                cv2.putText(frame, f"{label} {(conf*100):.0f}%", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, border_color, 2)

            frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

        cap.release()

    st.markdown("</div>", unsafe_allow_html=True)

# ================= TELEMETRY GRAPHICAL ANALYSIS =================
with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Intelligence Analytics")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)

        total_scans = len(df)
        fakes_count = len(df[df["Result"] == "FAKE"])
        reals_count = len(df[df["Result"] == "REAL"])

        c_sf1, c_sf2 = st.columns(2)
        c_sf1.metric("Analyzed Assets", total_scans)
        c_sf2.metric("Threat Vectors", fakes_count)

        # Matplotlib Professional Presentation Overhaul
        fig, ax = plt.subplots(figsize=(4, 4))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        slices = [fakes_count, reals_count]
        labels = ['Manipulated', 'Authentic']
        colors = ['#f43f5e', '#0d9488']
        
        # Guard against zero divisions safely
        if sum(slices) > 0:
            ax.pie(slices, labels=labels, colors=colors, autopct='%1.1f%%', 
                   textprops={'color': "#0f172a", 'weight': 'bold', 'size': 12}, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
    else:
        st.info("Awaiting telemetry deployment data strings.")
    st.markdown("</div>", unsafe_allow_html=True)

    # RECENT AUDIT LOGS
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧾 Secure Audit Logs")
    if st.session_state.history:
        for audit in st.session_state.history[-4:][::-1]:
            badge = "🔴" if audit['Result'] == "FAKE" else "🟢"
            st.write(f"`{audit['Timestamp']}` {badge} **{audit['Type']}** ➔ {audit['Result']} ({audit['Confidence']})")
    else:
        st.caption("Logs clear. No audit signals detected.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= HISTORICAL MATRIX SYSTEM =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📁 Historical Analysis Logs Database")

if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
else:
    st.caption("Database indices are currently uniform and empty.")
st.markdown("</div>", unsafe_allow_html=True)
