import scipy.signal
# Patch for librosa 0.8 compatibility with new scipy versions
if not hasattr(scipy.signal, 'hann'):
    import scipy.signal.windows
    scipy.signal.hann = scipy.signal.windows.hann

import librosa
from pydub import AudioSegment
import argparse
import os

def generate_multiple_loops(input_path, output_dir, max_loops=4, num_beats=16, repetitions=8, crossfade_ms=50):
    """
    Analyzes audio ONCE and generates multiple distinct loops from different parts of the song.
    Returns a list of generated file paths.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File '{input_path}' not found.")

    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Audio and Detect Beats (Heavy Operation, doing this ONLY ONCE)
    y, sr = librosa.load(input_path, sr=None)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    total_beats = len(beat_times)
    
    # If the track is too short for even one loop
    if total_beats < num_beats:
        raise ValueError(f"Track too short. Only {total_beats} beats detected.")
        
    # We want up to max_loops distinct starting beats, spaced out evenly.
    # Start the first one at beat 16 if possible to skip intro.
    start_offset = 16 if total_beats > 32 else 0
    available_beats = total_beats - start_offset - num_beats
    
    if available_beats <= 0:
        start_beats = [0]
    else:
        # Calculate spacing for 'max_loops'
        spacing = max(available_beats // max_loops, num_beats)
            
        start_beats = []
        curr_beat = start_offset
        while curr_beat + num_beats < total_beats and len(start_beats) < max_loops:
            start_beats.append(curr_beat)
            curr_beat += spacing
            
        if not start_beats:
            start_beats = [0]

    # 2. Pydub Slicing and Looping (Fast Operation)
    audio = AudioSegment.from_file(input_path)
    generated_files = []
    
    for i, start_beat in enumerate(start_beats):
        start_time_sec = beat_times[start_beat]
        end_time_sec = beat_times[start_beat + num_beats]
        
        start_time_ms = int(start_time_sec * 1000)
        end_time_ms = int(end_time_sec * 1000)
        
        loop_slice = audio[start_time_ms:end_time_ms]
        
        final_track = loop_slice
        for _ in range(repetitions - 1):
            final_track = final_track.append(loop_slice, crossfade=crossfade_ms)
            
        out_filename = f"loop_part_{i+1}.wav"
        out_path = os.path.join(output_dir, out_filename)
        final_track.export(out_path, format="wav")
        generated_files.append(out_path)
        
    return generated_files

def create_smooth_loop(input_path, output_path, start_beat=16, num_beats=16, repetitions=4, crossfade_ms=50):
    """
    Extracts a perfectly timed musical loop from an audio file and repeats it.
    """
    if not os.path.exists(input_path):
        print(f"❌ Error: File '{input_path}' not found.")
        return

    print(f"🎵 Loading audio for analysis: {input_path}")
    y, sr = librosa.load(input_path, sr=None)
    
    print("🥁 Detecting tempo and beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    if len(beat_times) < start_beat + num_beats:
        print(f"❌ Error: Audio is too short! Found {len(beat_times)} beats, but needed at least {start_beat + num_beats}.")
        return
        
    try:
        t_val = tempo[0]
    except (IndexError, TypeError):
        t_val = tempo
    print(f"⏱️ Estimated Tempo: {t_val:.1f} BPM")
    
    start_time_sec = beat_times[start_beat]
    end_time_sec = beat_times[start_beat + num_beats]
    
    print(f"✂️ Slicing audio from {start_time_sec:.2f}s (Beat {start_beat}) to {end_time_sec:.2f}s (Beat {start_beat + num_beats})")
    
    audio = AudioSegment.from_file(input_path)
    
    start_time_ms = int(start_time_sec * 1000)
    end_time_ms = int(end_time_sec * 1000)
    
    loop_slice = audio[start_time_ms:end_time_ms]
    
    print(f"🔄 Creating {repetitions} smooth repetitions with {crossfade_ms}ms crossfade...")
    
    final_track = loop_slice
    for _ in range(repetitions - 1):
        final_track = final_track.append(loop_slice, crossfade=crossfade_ms)
        
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
