# 🎧 Audet — Audio Intelligence for DJs & Producers

**Audet** is an open-source tool that detects **tempo (BPM)**, **musical key**, **mood**, and **genre** of your audio files using `librosa` and `Essentia`. It supports **Camelot/DJ key notation**, batch analysis, waveform previews, and drag-and-drop GUI — making it the ideal analyzer for DJs, producers, and audio engineers.

---

## 🚀 Features

### Core Analysis
- 🎼 **Key Detection** (Major/Minor + Confidence)
- 💽 **DJ Camelot Notation** (e.g., 8A, 9B)
- 🎵 **Tempo Detection** (BPM)
- 🎯 **Key Change Detection** over time
- 🎨 **Mood Estimation** (Energetic, Calm, Sad, Dark)
- 🎸 **Genre Classification** (Electronic, Ambient, Rock, Other)
- 📊 **Energy Level Analysis** throughout the track
- 🥁 **Beat Grid Analysis** with quantization detection

### Advanced Features
- 📂 **Batch Analysis** of Folders
- 🖱️ **GUI with Drag & Drop** support
- 🌊 **Waveform Plot Export** (PNG)
- 🔀 **Harmonic Mixing Suggestions**
- 🎯 **Mix Compatibility Analysis** between tracks
- 📋 **Smart Playlist Generation** with mood-based sorting
- 📊 **Detailed Analysis Reports** (HTML/JSON)
- 📈 **Interactive Visualizations** of key changes and energy levels

---

## 📦 Installation

```bash
pip install librosa matplotlib essentia tkinterdnd2
```

> ⚠️ `essentia` may require additional setup. See [Essentia install guide](https://essentia.upf.edu/documentation/).

---

## 🛠️ Usage

### CLI

```bash
python audet.py <yourfile.mp3|wav>
```

### Batch Folder

```bash
python audet.py /path/to/folder
```

### GUI Mode

Just run:

```bash
python audet_gui.py
```

The GUI provides three main tabs:

1. **Analysis Tab**
   - Drag and drop audio files or folders
   - View detailed analysis results
   - Export HTML/JSON reports
   - View waveform visualizations

2. **Playlist Generator**
   - Add multiple tracks
   - Select target mood
   - Generate optimized playlists
   - View transition scores

3. **Mix Compatibility**
   - Compare two tracks
   - Analyze tempo, key, and energy compatibility
   - Get overall mix score

---

## 🧠 Example Output

```
Analyzing: Echoes.wav
Estimated Tempo: 127.84 BPM
Estimated Key: F minor (Confidence: 0.93, Camelot: 4A)
Primary Mood: energetic
Genre: electronic
Key Changes: 3 detected
```

Also creates:
- `Echoes.wav_waveform.png` — waveform visualization
- `Echoes.wav_report.html` — detailed analysis report
- `analysis.json` — detailed analysis data
- `analysis.csv` — summary in spreadsheet format

---

## 📊 Analysis Reports

The HTML report includes:
- Basic track information
- Key changes over time (interactive chart)
- Mood analysis (radar chart)
- Energy levels throughout the track
- Beat grid analysis
- Genre classification

---

## 🔮 Roadmap

* [x] Tempo + Key detection
* [x] Camelot notation support
* [x] Folder batch processing
* [x] GUI frontend with drag & drop
* [x] Waveform export
* [x] Harmonic mixing hints
* [x] Key changes over time
* [x] Mood detection
* [x] Genre classification
* [x] Mix compatibility analysis
* [x] Smart playlist generation
* [ ] Upload to Mixcloud/Spotify crates (future)
* [ ] Real-time analysis during playback
* [ ] Advanced beat matching suggestions

---

## 👨‍💻 Contributing

1. Fork this repo
2. Make changes
3. Submit PR

All improvements to audio analysis, UI/UX, or ML mood modeling are welcome!

---

## 📜 License

MIT

---

## 🎛️ Powered By

* [Librosa](https://librosa.org/)
* [Essentia](https://essentia.upf.edu/)
* [TkinterDnD2](https://github.com/pmgagne/tkinterdnd2)
* [Plotly](https://plotly.com/)
* [Camelot Wheel](https://mixedinkey.com/camelot-wheel/)
