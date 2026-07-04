import scipy.signal
# Patch for librosa 0.8 compatibility with new scipy versions
if not hasattr(scipy.signal, 'hann'):
    import scipy.signal.windows
    scipy.signal.hann = scipy.signal.windows.hann

import librosa
from pydub import AudioSegment
import argparse
import os

def create_smooth_loop(input_path, output_path, start_beat=16, num_beats=16, repetitions=4, crossfade_ms=50):
    """
    Extracts a perfectly timed musical loop from an audio file and repeats it.
    
    Args:
        input_path (str): Path to the input audio (preferably an instrumental track).
        output_path (str): Path to save the looped output.
        start_beat (int): Which beat to start the loop on (to skip intros).
        num_beats (int): How many beats to include in the loop (multiples of 4 or 8 are best).
        repetitions (int): How many times to loop the clip.
        crossfade_ms (int): Duration of the crossfade in milliseconds to avoid clicks.
    """
    if not os.path.exists(input_path):
        print(f"❌ Error: File '{input_path}' not found.")
        return

    print(f"🎵 Loading audio for analysis: {input_path}")
    # Load audio with librosa for beat detection
    # sr=None preserves the original sampling rate
    y, sr = librosa.load(input_path, sr=None)
    
    print("🥁 Detecting tempo and beats...")
    # Get tempo and beat frames based on the onset envelope (transients/drums)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # Convert frames to exact timestamps (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    if len(beat_times) < start_beat + num_beats:
        print(f"❌ Error: Audio is too short! Found {len(beat_times)} beats, but needed at least {start_beat + num_beats}.")
        return
        
    try:
        t_val = tempo[0]
    except (IndexError, TypeError):
        t_val = tempo
    print(f"⏱️ Estimated Tempo: {t_val:.1f} BPM")
    
    # Calculate exactly where to slice (in seconds)
    start_time_sec = beat_times[start_beat]
    end_time_sec = beat_times[start_beat + num_beats]
    
    print(f"✂️ Slicing audio from {start_time_sec:.2f}s (Beat {start_beat}) to {end_time_sec:.2f}s (Beat {start_beat + num_beats})")
    
    # Now, load the high-quality audio with Pydub for manipulation
    # Pydub works in milliseconds
    audio = AudioSegment.from_file(input_path)
    
    start_time_ms = int(start_time_sec * 1000)
    end_time_ms = int(end_time_sec * 1000)
    
    # Extract the exact musical loop slice
    loop_slice = audio[start_time_ms:end_time_ms]
    
    print(f"🔄 Creating {repetitions} smooth repetitions with {crossfade_ms}ms crossfade...")
    
    # Create the repeating track
    final_track = loop_slice
    for _ in range(repetitions - 1):
        # Append the slice again, applying a crossfade to mask any clicks at the zero-crossing
        final_track = final_track.append(loop_slice, crossfade=crossfade_ms)
        
    # Export the final looped audio
    print(f"💾 Saving looped audio to: {output_path}")
    final_track.export(output_path, format="wav")
    print("✅ Done! You can now listen to your smooth loop.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create smooth loops from instrumental audio.")
    parser.add_argument("-i", "--input", required=True, help="Input audio file path (e.g., instruments.wav)")
    parser.add_argument("-o", "--output", default="looped_output.wav", help="Output audio file path")
    parser.add_argument("--start_beat", type=int, default=16, help="Beat index to start the slice (default: 16)")
    parser.add_argument("--num_beats", type=int, default=16, help="Number of beats in the loop (default: 16, which is 4 bars)")
    parser.add_argument("--repetitions", type=int, default=8, help="Number of times to repeat the loop (default: 8)")
    
    args = parser.parse_args()
    
    create_smooth_loop(
        input_path=args.input,
        output_path=args.output,
        start_beat=args.start_beat,
        num_beats=args.num_beats,
        repetitions=args.repetitions
    )
