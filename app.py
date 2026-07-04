import streamlit as st
import os
import subprocess
import shutil

# Set page configuration for a better user experience
st.set_page_config(page_title="AI Audio Separator", page_icon="🎵", layout="centered")

st.title("🎵 AI Audio Separator")
st.markdown("Separate vocals and instruments from any audio or video file using Spleeter's powerful AI.")

# Define working directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

# Ensure the directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# File uploader restricted to specific audio/video formats
uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "wav", "mp4", "m4a"])

if uploaded_file is not None:
    # Replace spaces with underscores to avoid command-line argument issues
    safe_filename = uploaded_file.name.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save the uploaded file securely to local disk
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"File uploaded successfully: `{safe_filename}`")
    
    # Process button
    if st.button("Separate Tracks", type="primary"):
        with st.spinner("Processing audio with AI... This may take a few minutes depending on the file size."):
            # Construct the Spleeter CLI command based on user specs
            # spleeter separate -p spleeter:2stems -o output [filename]
            command = [
                "spleeter", "separate", 
                "-p", "spleeter:2stems", 
                "-o", OUTPUT_DIR, 
                file_path
            ]
            
            try:
                # Execute Spleeter via subprocess
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                
                # Spleeter automatically creates a sub-directory named after the file (without extension)
                base_name = os.path.splitext(safe_filename)[0]
                spleeter_output_folder = os.path.join(OUTPUT_DIR, base_name)
                
                vocals_path = os.path.join(spleeter_output_folder, "vocals.wav")
                accompaniment_path = os.path.join(spleeter_output_folder, "accompaniment.wav")
                
                # Verify that the files were actually created
                if os.path.exists(vocals_path) and os.path.exists(accompaniment_path):
                    st.success("Separation complete!")
                    
                    st.markdown("### 📥 Download Tracks")
                    
                    # Create two columns for neat download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with open(vocals_path, "rb") as f:
                            st.download_button(
                                label="🎤 Download Vocals",
                                data=f,
                                file_name=f"{base_name}_vocals.wav",
                                mime="audio/wav"
                            )
                            
                    with col2:
                        with open(accompaniment_path, "rb") as f:
                            st.download_button(
                                label="🎸 Download Instruments",
                                data=f,
                                file_name=f"{base_name}_instruments.wav",
                                mime="audio/wav"
                            )
                    
                    st.markdown("---")
                    st.markdown("### 🔁 Rhythmic Loop Generator")
                    st.markdown("Extract perfect rhythmic loops from the instrumental track automatically.")
                    
                    if st.button("Generate Instrumental Loops", type="secondary"):
                        with st.spinner("Analyzing beats and generating up to 4 distinct loops... (This takes about a minute)"):
                            try:
                                from beat_looper import generate_multiple_loops
                                
                                loop_output_dir = os.path.join(spleeter_output_folder, "loops")
                                generated_loops = generate_multiple_loops(
                                    input_path=accompaniment_path, 
                                    output_dir=loop_output_dir,
                                    max_loops=4,
                                    num_beats=16,
                                    repetitions=8
                                )
                                
                                if generated_loops:
                                    st.success(f"Generated {len(generated_loops)} loops successfully!")
                                    
                                    # Display players and downloads in columns
                                    # Since there can be up to 4, we chunk them into rows of 2 for better UI
                                    for row_idx in range(0, len(generated_loops), 2):
                                        row_loops = generated_loops[row_idx:row_idx+2]
                                        cols = st.columns(len(row_loops))
                                        for col_idx, loop_path in enumerate(row_loops):
                                            loop_num = row_idx + col_idx + 1
                                            with cols[col_idx]:
                                                st.markdown(f"**Loop {loop_num}**")
                                                st.audio(loop_path, format="audio/wav")
                                                with open(loop_path, "rb") as lf:
                                                    st.download_button(
                                                        label=f"⬇️ Download Loop {loop_num}",
                                                        data=lf,
                                                        file_name=f"{base_name}_loop_{loop_num}.wav",
                                                        mime="audio/wav",
                                                        key=f"dl_loop_{loop_num}"
                                                    )
                                else:
                                    st.warning("No loops could be generated. The track might be too short.")
                            except Exception as e:
                                st.error(f"Failed to generate loops: {str(e)}")
                else:
                    st.error("Separation failed: Output files not found. Please ensure FFmpeg is installed and accessible.")
                    
            except subprocess.CalledProcessError as e:
                st.error("An error occurred during separation.")
                with st.expander("Show error details"):
                    st.code(e.stderr)
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

# Add a small footer
st.markdown("---")
st.markdown("<small>Powered by Streamlit, Spleeter, and FFmpeg.</small>", unsafe_allow_html=True)
