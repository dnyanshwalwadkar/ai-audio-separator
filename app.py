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
    if not (os.path.exists(vocals_path) and os.path.exists(accompaniment_path)):
        if st.button("Separate Tracks", type="primary"):
            with st.spinner("Processing audio with AI... This may take a few minutes depending on the file size."):
                # Construct the Spleeter CLI command based on user specs
                command = [
                    "spleeter", "separate", 
                    "-p", "spleeter:2stems", 
                    "-o", OUTPUT_DIR, 
                    file_path
                ]
                
                try:
                    # Execute Spleeter via subprocess
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    st.rerun() # Refresh the page to show the download buttons
                except subprocess.CalledProcessError as e:
                    st.error("An error occurred during separation.")
                    with st.expander("Show error details"):
                        st.code(e.stderr)
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
                    
    # Display results if they exist on disk (fixes Streamlit state issues)
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
        
        loop_output_dir = os.path.join(spleeter_output_folder, "loops")
        
        if st.button("Generate Instrumental Loops", type="secondary"):
            with st.spinner("Analyzing beats and generating up to 4 distinct loops... (This takes about a minute)"):
                try:
                    from beat_looper import generate_multiple_loops
                    
                    generate_multiple_loops(
                        input_path=accompaniment_path, 
                        output_dir=loop_output_dir,
                        max_loops=4,
                        num_beats=16,
                        repetitions=8
                    )
                    st.rerun() # Refresh to show the new audio files
                except Exception as e:
                    st.error(f"Failed to generate loops: {str(e)}")
                    
        # Check if loops exist on disk and display them unconditionally
        if os.path.exists(loop_output_dir):
            generated_loops = [os.path.join(loop_output_dir, f) for f in os.listdir(loop_output_dir) if f.endswith('.wav')]
            generated_loops.sort()
            
            if generated_loops:
                st.success(f"Generated {len(generated_loops)} loops successfully!")
                
                # Display players and downloads in columns
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

# Add a small footer
st.markdown("---")
st.markdown("<small>Powered by Streamlit, Spleeter, and FFmpeg.</small>", unsafe_allow_html=True)
