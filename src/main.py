# code by Kam 
from yt_dlp import YoutubeDL

from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
import time
from time import sleep
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
import sys
from gtts import gTTS
import glob, os
import shutil
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# ============================================
# ✅ SET FFMPEG
# ============================================
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    
    ffmpeg_dir = base_path / "ffmpeg"
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
    ffprobe_exe = ffmpeg_dir / "ffprobe.exe"
    
    if not ffmpeg_exe.exists():
        raise FileNotFoundError(f"Không tìm thấy FFmpeg tại: {ffmpeg_exe}")
    if not ffprobe_exe.exists():
        raise FileNotFoundError(f"Không tìm thấy FFprobe tại: {ffprobe_exe}")
    
    return str(ffmpeg_exe), str(ffprobe_exe)

try:
    ffmpeg_exe, ffprobe_exe = get_ffmpeg_path()
    os.environ["PATH"] = str(Path(ffmpeg_exe).parent) + os.pathsep + os.environ.get("PATH", "")
except FileNotFoundError as e:
    print(f"❌ {e}")
    sys.exit(1)

from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub.effects import speedup

AudioSegment.converter = ffmpeg_exe
AudioSegment.ffprobe = ffprobe_exe

# ============================================
# ✅ FIX (1): LẤY VIDEO ID BẰNG yt_dlp
# ============================================
def get_video_id(url):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['id']

url = str(input("Link youtube video: "))
video_id = get_video_id(url)

# ============================================

current_dir = Path(__file__).parent.resolve()
segments_dir = current_dir / "segments"
segments_dir.mkdir(exist_ok=True, parents=True)

cache_dir = current_dir / "tts_cache"
cache_dir.mkdir(exist_ok=True, parents=True)

dubbing_dir = current_dir / "dubbing"
dubbing_dir.mkdir(parents=True, exist_ok=True)

tmp_dir = current_dir / "../runtime/tmp"

file_name = "video.mp4"
video_path = tmp_dir / file_name

if tmp_dir.exists():
    shutil.rmtree(tmp_dir)
tmp_dir.mkdir(exist_ok=True)

max_threads = min(16, os.cpu_count() or 4) 

def get_video():
    print("Đang lấy video gốc ▶️ ...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': str(video_path),
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Lấy video hoàn tất✅")

# ============================================
# ✅ FIX (2): SỬA API LẤY PHỤ ĐỀ
# ============================================
def get_caption():
    print("Đang lấy phụ đề ...")

    # =============================
    # 1. THỬ youtube_transcript_api
    # =============================
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        print("📜 Danh sách phụ đề:")
        for t in transcripts:
            print(" -", t.language_code, "(auto)" if t.is_generated else "")

        # Ưu tiên en thường → auto → bất kỳ
        try:
            transcript = transcripts.find_transcript(['en', 'en-US'])
        except:
            try:
                transcript = transcripts.find_generated_transcript(['en'])
            except:
                transcript = list(transcripts)[0]

        # retry fetch (rất quan trọng)
        for _ in range(3):
            try:
                data = transcript.fetch()
                if data:
                    break
            except Exception as e:
                print("⚠️ retry fetch...", e)
                sleep(1)
        else:
            data = []

        if data:
            caption = {}
            for i in data:
                caption[i['start']] = i['text'].replace('\n', ' ')
            print("✅ Lấy phụ đề bằng API thành công!")
            return caption

    except Exception as e:
        print("⚠️ API lỗi:", e)

    # =============================
    # 2. FALLBACK: yt-dlp
    # =============================
    print("⚠️ Chuyển sang yt-dlp...")

    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'outtmpl': str(tmp_dir / "sub")
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # tìm file .vtt
        vtt_files = list(tmp_dir.glob("*.vtt"))

        if not vtt_files:
            print("❌ Không tìm thấy file .vtt")
            return {}

        vtt_file = vtt_files[0]
        print(f"📄 Đọc {vtt_file.name}")

        # parse vtt
        caption = {}
        with open(vtt_file, encoding="utf-8") as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if "-->" in lines[i]:
                try:
                    # parse thời gian: 00:01:23.456
                    t = lines[i].split("-->")[0].strip()
                    h, m, s = t.split(":")
                    start = int(h)*3600 + int(m)*60 + float(s)

                    text = lines[i+1].strip()
                    if text:
                        caption[start] = text
                except:
                    continue

        if caption:
            print("✅ Lấy phụ đề bằng yt-dlp thành công!")
        else:
            print("❌ Parse .vtt thất bại")

        return caption

    except Exception as e:
        print("❌ yt-dlp cũng thất bại:", e)
        return {}
# ============================================

def translate_all_captions(caption):
    print("🌐 Đang dịch...")
    translated_map = {}
    translator = GoogleTranslator(source='auto', target='vi')

    def translate_safe(text):
        try:
            return translator.translate(text)
        except Exception:
            return text

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(translate_safe, text): start for start, text in caption.items()}

        for future in as_completed(futures):
            start = futures[future]
            translated_map[start] = future.result()

    return translated_map

# (phần còn lại giữ nguyên)

def play_video(video_path: str):
    app = QApplication(sys.argv)

    # --- Cửa sổ phát video ---
    window = QWidget()
    window.setWindowTitle("🎬 Trình phát video")
    layout = QVBoxLayout(window)

    video_widget = QVideoWidget()
    layout.addWidget(video_widget)

    slider = QSlider(Qt.Orientation.Horizontal)
    layout.addWidget(slider)

    btn_play = QPushButton("▶ Phát / Tạm dừng")
    layout.addWidget(btn_play)

    # --- Thiết lập player ---
    player = QMediaPlayer()
    audio = QAudioOutput()
    player.setAudioOutput(audio)
    player.setVideoOutput(video_widget)
    player.setSource(QUrl.fromLocalFile(str(Path(video_path).resolve())))

    def toggle_play():
        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.pause()
        else:
            player.play()
    btn_play.clicked.connect(toggle_play)

    # --- Cập nhật thanh trượt ---
    player.durationChanged.connect(lambda d: slider.setRange(0, d))
    player.positionChanged.connect(lambda p: slider.setValue(p))
    slider.sliderMoved.connect(lambda v: player.setPosition(v))

    # --- Lấy thời gian hiện tại (làm tròn đến phần nghìn giây) ---
    player.play()
    window.show()
    sys.exit(app.exec())

# Khai báo hằng số tốc độ (Ví dụ: nhanh hơn 40%)
SPEED_FACTOR = 1.9

# ... (Giữ nguyên các import và thiết lập FFmpeg) ...

# ... (Giữ nguyên các hàm get_video, get_caption, play_video) ...

def make_dubbing_from_map(segments, speed_factor):
    # ✅ Xóa thư mục segments cũ và tạo mới
    if segments_dir.exists():
        shutil.rmtree(segments_dir)
    segments_dir.mkdir(exist_ok=True)
    # ... (Giữ nguyên phần thiết lập thư mục và tính max_duration) ...
    
    sorted_segments = sorted(segments.items())
    
    if sorted_segments:
        last_start = sorted_segments[-1][0]
        # Sử dụng 15 giây buffer là hợp lý
        max_duration = int((last_start * 1000) + 15000)
    else:
        max_duration = 0
    
    final_audio = AudioSegment.silent(duration=max_duration)

    for i, (start, text) in enumerate(sorted_segments):
        print(f"Đang xử lý segment {i+1}/{len(sorted_segments)}: {start}s - {text[:30]}...")
        
        cache_path = cache_dir / (hashlib.md5(text.encode()).hexdigest() + ".mp3")

        if cache_path.exists():
            audio = AudioSegment.from_mp3(str(cache_path))
        else:
            tts = gTTS(text=text, lang='vi')
            tts.save(str(cache_path))
            audio = AudioSegment.from_mp3(str(cache_path))
        
        # 3.✅ Tăng tốc độ đọc bằng speedup
        fast_audio = speedup(audio, playback_speed=speed_factor, chunk_size=50, crossfade=25)
        
        # 4. Overlay chính xác tại vị trí start
        start_ms = int(start * 1000)
        final_audio = final_audio.overlay(fast_audio, position=start_ms)

    output_path = tmp_dir / "voice_full.mp3"
    final_audio.export(str(output_path), format="mp3")
    print("✅ Đã tạo xong voice_full.mp3 với tốc độ đọc đã tăng.")

get_video()
caption = get_caption()                   # map tiếng Anh
vi_caption = translate_all_captions(caption)  # map tiếng Việt
# ✅ TRUYỀN THAM SỐ TỐC ĐỘ VÀO HÀM
make_dubbing_from_map(vi_caption, SPEED_FACTOR) 

# ... (Giữ nguyên hàm dubbing_video) ...
def dubbing_video():
    # Dọn thư mục đầu ra
    if dubbing_dir.exists():
        shutil.rmtree(dubbing_dir)
    dubbing_dir.mkdir(exist_ok=True)

    # Đảm bảo tmp_dir tồn tại để tránh lỗi file tạm
    tmp_dir.mkdir(exist_ok=True)

    video_path = tmp_dir / "video.mp4"
    audio_path = tmp_dir / "voice_full.mp3"
    output_path = dubbing_dir / "dubbing_video.mp4"
    temp_audio_path = tmp_dir / "_temp_audio.mp4"

    print("🎞️ Đang ghép âm thanh và video...")

    video = VideoFileClip(str(video_path))
    audio = AudioFileClip(str(audio_path))
    final = video.set_audio(audio)

    # Ghi video và đảm bảo xóa mọi file tạm sau khi xong
    final.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(temp_audio_path),  # file tạm riêng biệt
        remove_temp=True,                     # moviepy sẽ tự xóa nó
        threads=max_threads,
        verbose=True,                        # tắt log ffmpeg
        logger='bar'                           # không cần logger 'bar'
    )

    # Nếu file tạm vẫn còn (hiếm gặp), xóa thủ công
    if temp_audio_path.exists():
        try:
            temp_audio_path.unlink()
            print("🧹 Đã xóa file tạm còn sót lại.")
        except Exception as e:
            print(f"⚠️ Không thể xóa file tạm: {e}")

    print("✅ Xuất video hoàn tất (không còn file TEMP_MPY_wvf_snd.mp4).")

dubbing_video()

# === SAO CHÉP VIDEO SANG DOWNLOAD ===
downloads_path = Path.home() / "Downloads"
downloads_path.mkdir(exist_ok=True)

copy_path = downloads_path / "dubbing_video.mp4"

try:
    shutil.copy2(dubbing_dir / "dubbing_video.mp4", copy_path)
    print(f"📂 Đã sao chép bản dubbing sang: {copy_path}")
except Exception as e:
    print(f"⚠️ Không thể sao chép sang thư mục Downloads: {e}")

# === XÓA CACHE CŨ ===
def clean_old_cache(days=7):
    cutoff = time.time() - days * 86400
    removed = 0
    for f in cache_dir.glob("*.mp3"):
        if f.stat().st_mtime < cutoff:
            try:
                f.unlink()
                removed += 1
            except Exception:
                pass
    if removed:
        print(f"🧹 Đã xóa {removed} file cache cũ hơn {days} ngày.")

clean_old_cache()

# === PHÁT VIDEO ===
play_video(str(copy_path))