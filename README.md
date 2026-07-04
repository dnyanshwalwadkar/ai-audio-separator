# 🎵 AI Audio Separator

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.39+-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Spleeter-orange.svg" alt="Spleeter">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</div>

<br>

A full-stack, single-page web application built with Streamlit that separates audio and video files into distinct vocal and instrumental tracks using advanced Deep Learning.

## ✨ Features
- **Multi-Format Support**: Upload `.mp3`, `.wav`, `.mp4`, or `.m4a` files.
- **AI-Powered Separation**: Uses Deezer's Spleeter backend for state-of-the-art source separation.
- **Instant Downloads**: Automatically generates high-quality `vocals.wav` and `accompaniment.wav` files for immediate download.
- **Secure File Handling**: Sanitizes filenames and manages local file storage safely.

---

## 🚀 Inputs & Outputs Example

To use the tool, you simply upload a mixed audio file, and the AI extracts the isolated components. You can listen to the actual files below:

**Input:**
- [Ajit_Kadkade_-_Vithoba_Rakhumai.mp3](examples/Ajit_Kadkade_-_Vithoba_Rakhumai_-_(320_Kbps).mp3) (Mixed Audio Track)

**Outputs:**
- 🎤 [Ajit_Kadkade_vocals.wav](examples/vocals.wav) (Isolated Vocals)
- 🎸 [Ajit_Kadkade_instruments.wav](examples/instruments.wav) (Isolated Accompaniment / Instruments)

---

## 🧠 Model Architecture

This application utilizes a **U-Net Convolutional Neural Network (CNN)** architecture optimized for audio source separation. 

### How it works (The U-Net Design)
1. **Encoder (Downsampling)**: The network takes the magnitude spectrogram of the mixed audio and passes it through a series of 2D Convolutional layers. Each layer halves the spatial dimensions while doubling the feature channels, effectively compressing the audio into a dense, high-level latent representation.
2. **Bottleneck**: The lowest layer captures the deepest temporal and spectral correlations of the audio track.
3. **Decoder (Upsampling)**: Transposed convolutions (deconvolutions) reconstruct the audio back to its original dimensions, gradually restoring the time and frequency resolution.
4. **Skip Connections**: To prevent the loss of fine-grained spectral details (which often occurs during deep compression), skip connections link the encoder layers directly to their corresponding decoder layers. This ensures crisp, high-fidelity audio reconstruction by passing low-level phase and magnitude data directly to the output layers.

---

## 📐 Mathematical Formulation

The separation process relies on time-frequency masking of spectrograms.

### 1. Short-Time Fourier Transform (STFT)
The input time-domain audio signal $x(t)$ is first converted into a time-frequency representation (spectrogram) using STFT:
$$X(t, f) = \text{STFT}(x(t))$$
where $X(t, f)$ is the complex-valued spectrogram representing magnitude and phase.

### 2. Neural Network Mask Generation
The U-Net model takes the magnitude spectrogram $|X(t, f)|$ and estimates a **soft mask** $M_i(t, f)$ for each source $i$ (e.g., vocals, accompaniment).
The mask values are bounded between 0 and 1 using a Sigmoid activation function:
$$M_i(t, f) \in [0, 1]$$

### 3. Spectrogram Masking
The estimated mask is applied to the original mixed spectrogram via element-wise multiplication (Hadamard product):
$$\hat{S}_i(t, f) = M_i(t, f) \odot X(t, f)$$
This filters out the frequencies that do not belong to the target source, isolating the specific stems.

### 4. Inverse STFT (ISTFT)
Finally, the estimated source spectrogram $\hat{S}_i(t, f)$ is converted back into a time-domain audio waveform using the Inverse STFT:
$$\hat{s}_i(t) = \text{ISTFT}(\hat{S}_i(t, f))$$

---

## 🛠️ Local Installation

### Prerequisites
- Python 3.9+
- FFmpeg installed on your system (Required for media processing)

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/dnyanshwalwadkar/ai-audio-separator.git
   cd ai-audio-separator
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## 📩 Contact & Weights

The pre-trained neural network weights for the standard Spleeter model are automatically downloaded during the first run. 

However, if you require specific **fine-tuned weights**, **customized architectures**, or have any deeper technical/business inquiries regarding this implementation, please reach out directly:

**Email:** [dnyaneshwalwadkar10@gmail.com](mailto:dnyaneshwalwadkar10@gmail.com)
