# 🎬 YouTube Video Dubbing Tool
---

## 📌 Overview

This is a Python-based tool that automatically:
- Downloads videos from YouTube
- Extracts subtitles (API first, fallback with yt-dlp)
- Translates them into Vietnamese
- Converts text to speech (TTS)
- Merges audio back into the video

---

## 🚀 Features

- 📥 Download video using yt-dlp  
- 🧾 Extract subtitles (API + fallback)  
- 🌐 Multi-threaded translation  
- 🔊 Text-to-Speech (gTTS)  
- ⚡ Speed adjustment  
- 🎞️ Video + audio merging  
- ▶️ Built-in player (PyQt6)  

---

## ⚠️ Important Notes

### ❗ Video MUST have subtitles
- Only works if subtitles exist
- Supports:
  - English subtitles
  - Auto-generated subtitles  

---

## 📁 Project Structure

```
tts_dubbing_youtube/
│
├── src/
│ ├── main.py
│ └── ffmpeg/ # bundled FFmpeg binaries
│     ├── ffmpeg.exe
│     └── ffprobe.exe
│
├── requirements.txt
├── README.md
├── README.vi.md
└── .gitignore
```

---

## ⚙️ Requirements

- Python 3.9+
- ❌ No need to install FFmpeg manually  
  (already bundled in `src/ffmpeg/`)

---

## 📦 Installation
```bash
git clone https://github.com/your-username/tts_dubbing_youtube.git
cd tts_dubbing_youtube
pip install -r requirements.txt
```
## ▶️ Usage
```bash
python src/main.py
```
## 🛠️ Technologies
- yt-dlp
- youtube-transcript-api
- deep-translator
- gTTS
- pydub
- moviepy
- PyQt6
- FFmpeg (bundled)
## ⚠️ Limitations
- Imperfect audio sync
- Possible overlap
- TTS quality is limited
- Translation may be inaccurate
## 🔮 Future Improvements
- Better alignment (DTW)
- Whisper ASR
- High-quality TTS
- Smart timing
## 👤 Author

[Kam](https://github.com/1TM-1)
---
# 🎬 Công cụ lồng tiếng video YouTube

---

## 📌 Giới thiệu

Công cụ Python giúp:
- Tải video YouTube
- Lấy phụ đề (API + fallback yt-dlp)
- Dịch sang tiếng Việt
- Tạo giọng nói (TTS)
- Ghép lại thành video

---

## 🚀 Tính năng

- 📥 Tải video bằng yt-dlp  
- 🧾 Lấy phụ đề (API + fallback)  
- 🌐 Dịch đa luồng  
- 🔊 Text-to-Speech (gTTS)  
- ⚡ Tăng tốc đọc  
- 🎞️ Ghép audio + video  
- ▶️ Trình phát video  

---

## ⚠️ Lưu ý quan trọng

### ❗ Video phải có phụ đề
- Tool chỉ hoạt động khi có phụ đề  
- Hỗ trợ:
  - Phụ đề tiếng Anh  
  - Phụ đề tự động  

---

## 📁 Cấu trúc project

```
tts_dubbing_youtube/
│
├── src/
│ ├── main.py
│ └── ffmpeg/ # FFmpeg đã tích hợp sẵn
│     ├── ffmpeg.exe
│     └── ffprobe.exe
│
├── requirements.txt
├── README.md
├── README.vi.md
└── .gitignore
```

---

## ⚙️ Yêu cầu

- Python 3.9+
- ❌ Không cần cài FFmpeg  
  (đã có sẵn trong project)

---

## 📦 Cài đặt

```bash
git clone https://github.com/your-username/tts_dubbing_youtube.git
cd tts_dubbing_youtube
pip install -r requirements.txt
```
## ▶️ Cách chạy

```bash
python src/main.py
```
## 🛠️ Công nghệ

- yt-dlp
- youtube-transcript-api
- deep-translator
- gTTS
- pydub
- moviepy
- PyQt6
- FFmpeg (đã tích hợp)
## ⚠️ Hạn chế

- Audio có thể lệch
- Có thể bị chồng tiếng
- Giọng gTTS chưa tự nhiên
- Dịch chưa chính xác hoàn toàn
## 🔮 Hướng phát triển

- Căn chỉnh tốt hơn (DTW)
- Dùng Whisper
- TTS xịn hơn
- Timing thông minh
## 👤 Tác giả

[Kam](https://github.com/1TM-1)
---
