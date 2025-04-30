import whisper
import torch
import srt
import ffmpeg
import datetime
import os
from tkinter import Tk, filedialog

# ✅ Open file selection dialog
def select_file():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        filetypes=[("Video files", ("*.mp4", "*.mov", "*.avi"))]
    )
    return file_path

# ✅ Generate output file names
def generate_file_names(video_file_path):
    base_name = os.path.splitext(os.path.basename(video_file_path))[0]
    folder_path = os.path.dirname(video_file_path)
    english_srt_file = os.path.join(folder_path, f"{base_name}_english.srt")
    output_video_with_subs = os.path.join(folder_path, f"{base_name}_with_english_subs.mp4")
    return english_srt_file, output_video_with_subs

# ✅ Let the user select a video file
video_file = select_file()
if not video_file:
    print("No file selected. Exiting program.")
    exit()

# ✅ Generate output filenames
english_srt_file, output_video_with_subs = generate_file_names(video_file)

# ✅ Auto-select device (CPU only in this case)
device = "cpu"  # You can change to "cuda" or "mps" if available
print(f"Using device: {device}")

# ✅ Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("base", device=device)

# ✅ Transcribe video audio to English
print("Transcribing audio to English subtitles...")
result = model.transcribe(video_file)

# ✅ Convert segments to SRT subtitles
def make_srt(segments):
    subtitles = []
    for i, segment in enumerate(segments):
        start = datetime.timedelta(seconds=segment['start'])
        end = datetime.timedelta(seconds=segment['end'])
        text = segment['text'].strip()
        subtitles.append(srt.Subtitle(index=i + 1, start=start, end=end, content=text))
    return subtitles

# ✅ Save English subtitles to SRT file
english_subs = make_srt(result['segments'])
with open(english_srt_file, "w", encoding="utf-8") as f:
    f.write(srt.compose(english_subs))

print(f"✅ English subtitles saved to → {english_srt_file}")

# ✅ Overlay English subtitles onto video using ffmpeg
print("Adding English subtitles to video...")
ffmpeg.input(video_file).output(
    output_video_with_subs,
    vf=f"subtitles={english_srt_file}"
).run(overwrite_output=True)

print("Done!")
print(f"Final video file: {output_video_with_subs}")