# 🎧 Audet — Audio Intelligence for DJs & Producers

**Audet** is an open-source tool that detects **tempo (BPM)** and **musical key** of your audio files using `librosa` and `Essentia`. It supports **Camelot/DJ key notation**, batch analysis, waveform previews, and drag-and-drop GUI — making it the ideal analyzer for DJs, producers, and audio engineers.

---

## 🚀 Features

- 🎼 **Key Detection** (Major/Minor + Confidence)
- 💽 **DJ Camelot Notation** (e.g., 8A, 9B)
- 🎵 **Tempo Detection** (BPM)
- 📂 **Batch Analysis** of Folders
- 🖱️ **GUI with Drag & Drop** support
- 🌊 **Waveform Plot Export** (PNG)
- 🔀 **Harmonic Mixing Suggestions**
- 😎 **(Coming soon)** Track Mood Estimation (Energetic, Calm, Sad…)
- ⏳ **(Planned)** Key Change Detection over Time

---

## 📦 Installation

```bash
pip install librosa matplotlib essentia tkinterdnd2
````

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

Then drag and drop audio files or folders into the window.

---

## 🧠 Example Output

```
Analyzing: Echoes.wav
Estimated Tempo: 127.84 BPM
Estimated Key: F minor (Confidence: 0.93, Camelot: 4A)
```

Also creates a file:

```
Echoes.wav_waveform.png
```

---

## 📁 Output Files

* `analysis.json` — detailed analysis
* `analysis.csv` — human-readable summary
* `<filename>_waveform.png` — waveform visualization

---

## 🔮 Roadmap

* [x] Tempo + Key detection
* [x] Camelot notation support
* [x] Folder batch processing
* [x] GUI frontend with drag & drop
* [x] Waveform export
* [ ] Harmonic mixing hints
* [ ] Key changes over time
* [ ] Mood detection via ML
* [ ] Upload to Mixcloud/Spotify crates (future)

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
* [Camelot Wheel](https://mixedinkey.com/camelot-wheel/)
