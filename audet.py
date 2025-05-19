import sys
import os
import json
import csv
import librosa
import numpy as np
import matplotlib.pyplot as plt
from essentia.standard import MonoLoader, KeyExtractor
from pathlib import Path
import webbrowser
from datetime import datetime

# Camelot wheel mapping
CAMELOT_MAP = {
    'C major': '8B', 'G major': '9B', 'D major': '10B', 'A major': '11B', 'E major': '12B',
    'B major': '1B', 'F# major': '2B', 'C# major': '3B', 'G# major': '4B', 'D# major': '5B',
    'A# major': '6B', 'F major': '7B',
    'A minor': '8A', 'E minor': '9A', 'B minor': '10A', 'F# minor': '11A', 'C# minor': '12A',
    'G# minor': '1A', 'D# minor': '2A', 'A# minor': '3A', 'F minor': '4A', 'C minor': '5A',
    'G minor': '6A', 'D minor': '7A'
}

# Mood mapping
MOODS = {
    'energetic': ['energetic', 'happy', 'excited', 'upbeat'],
    'calm': ['calm', 'relaxed', 'peaceful', 'serene'],
    'sad': ['sad', 'melancholic', 'emotional', 'nostalgic'],
    'dark': ['dark', 'mysterious', 'intense', 'dramatic']
}

def get_harmonic_matches(camelot_key):
    """Get harmonically compatible keys based on Camelot wheel"""
    number = int(camelot_key[:-1])
    letter = camelot_key[-1]
    
    matches = [
        camelot_key,  # Same key
        f"{number}{'B' if letter == 'A' else 'A'}",  # Parallel key
        f"{(number % 12) + 1}{letter}",  # Next clockwise
        f"{((number - 2) % 12) + 1}{letter}",  # Previous counter-clockwise
    ]
    return matches

def detect_tempo(y, sr):
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo.item()

def detect_key(filename):
    audio = MonoLoader(filename=filename)()
    key, scale, strength = KeyExtractor()(audio)
    key_str = f"{key} {scale}"
    camelot = CAMELOT_MAP.get(key_str, "Unknown")
    return key_str, camelot, strength

def detect_key_changes(y, sr, hop_length=512):
    """Detect key changes over time using sliding window analysis"""
    window_size = int(4 * sr)
    hop_samples = int(2 * sr)
    
    key_changes = []
    times = []
    
    for i in range(0, len(y) - window_size, hop_samples):
        window = y[i:i + window_size]
        key, scale, strength = KeyExtractor()(window)
        key_str = f"{key} {scale}"
        camelot = CAMELOT_MAP.get(key_str, "Unknown")
        
        time = i / sr
        key_changes.append({
            'time': time,
            'key': key_str,
            'camelot': camelot,
            'confidence': float(strength)
        })
        times.append(time)
    
    return key_changes

def estimate_mood(y, sr):
    """Estimate the mood of the track using audio features"""
    tempo = detect_tempo(y, sr)
    
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)[0]
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    rhythm_features = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    
    energy = np.mean(spectral_centroid)
    brightness = np.mean(spectral_rolloff)
    contrast = np.mean(spectral_contrast)
    rhythm_stability = np.std(rhythm_features)
    
    if tempo > 130 and energy > 0.7:
        mood = 'energetic'
    elif tempo < 100 and energy < 0.4:
        mood = 'calm'
    elif contrast > 0.6 and brightness < 0.5:
        mood = 'dark'
    else:
        mood = 'sad'
    
    mood_scores = {
        'energetic': min(1.0, (tempo/180) * (energy/0.8)),
        'calm': min(1.0, (1 - tempo/180) * (1 - energy/0.8)),
        'dark': min(1.0, (contrast/0.8) * (1 - brightness/0.8)),
        'sad': min(1.0, (1 - contrast/0.8) * (brightness/0.8))
    }
    
    return {
        'primary_mood': mood,
        'mood_scores': mood_scores,
        'features': {
            'tempo': float(tempo),
            'energy': float(energy),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'rhythm_stability': float(rhythm_stability)
        }
    }

def analyze_beat_grid(y, sr):
    """Analyze the beat grid and detect beat positions"""
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    beat_strength = librosa.util.normalize(onset_env[beat_frames])
    
    return {
        'tempo': float(tempo.item()) if hasattr(tempo, 'item') else float(tempo),
        'beat_times': beat_times.tolist(),
        'beat_strength': beat_strength.tolist(),
        'is_quantized': np.std(np.diff(beat_times)) < 0.1
    }

def analyze_energy_levels(y, sr, segment_length=1.0):
    """Analyze energy levels throughout the track"""
    segment_samples = int(segment_length * sr)
    energy_levels = []
    
    for i in range(0, len(y), segment_samples):
        segment = y[i:i + segment_samples]
        if len(segment) == segment_samples:
            rms = librosa.feature.rms(y=segment)[0]
            energy_levels.append({
                'time': i / sr,
                'energy': float(np.mean(rms)),
                'peak': float(np.max(rms))
            })
    
    return {
        'segments': energy_levels,
        'average_energy': float(np.mean([s['energy'] for s in energy_levels])),
        'energy_variance': float(np.var([s['energy'] for s in energy_levels]))
    }

def classify_genre(y, sr):
    """Classify the genre using audio features"""
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    
    mfcc_mean = np.mean(mfccs, axis=1)
    mfcc_std = np.std(mfccs, axis=1)
    
    if np.mean(spectral_centroid) > 0.7 and np.std(mfcc_mean) > 2.0:
        genre = 'electronic'
    elif np.mean(spectral_rolloff) < 0.5 and np.mean(mfcc_mean) < 0:
        genre = 'ambient'
    elif np.std(mfcc_std) > 1.5:
        genre = 'rock'
    else:
        genre = 'other'
    
    return {
        'genre': genre,
        'confidence': float(np.mean(mfcc_std)),
        'features': {
            'mfcc_mean': mfcc_mean.tolist(),
            'mfcc_std': mfcc_std.tolist(),
            'spectral_centroid': float(np.mean(spectral_centroid)),
            'spectral_rolloff': float(np.mean(spectral_rolloff))
        }
    }

def analyze_mix_compatibility(track1, track2):
    """Analyze how well two tracks would mix together"""
    y1, sr1 = librosa.load(track1, sr=None)
    y2, sr2 = librosa.load(track2, sr=None)
    
    analysis1 = analyze_audio(track1)
    analysis2 = analyze_audio(track2)
    
    tempo_diff = abs(analysis1['tempo'] - analysis2['tempo'])
    key_compatibility = analysis1['camelot'] in analysis2['harmonic_matches']
    
    energy1 = analyze_energy_levels(y1, sr1)
    energy2 = analyze_energy_levels(y2, sr2)
    energy_diff = abs(energy1['average_energy'] - energy2['average_energy'])
    
    return {
        'tempo_compatibility': 1.0 - min(1.0, tempo_diff / 20.0),
        'key_compatibility': key_compatibility,
        'energy_compatibility': 1.0 - min(1.0, energy_diff / 0.5),
        'overall_score': float(np.mean([
            1.0 - min(1.0, tempo_diff / 20.0),
            float(key_compatibility),
            1.0 - min(1.0, energy_diff / 0.5)
        ]))
    }

def generate_playlist(tracks, target_mood=None, target_energy=None):
    """Generate a playlist based on mood and energy flow"""
    analyzed_tracks = []
    for track in tracks:
        analysis = analyze_audio(track)
        analyzed_tracks.append({
            'path': track,
            'analysis': analysis
        })
    
    analyzed_tracks.sort(key=lambda x: x['analysis']['mood']['features']['energy'])
    
    if target_mood:
        analyzed_tracks.sort(key=lambda x: x['analysis']['mood']['mood_scores'][target_mood], reverse=True)
    
    playlist = []
    for i in range(len(analyzed_tracks)):
        if i > 0:
            compatibility = analyze_mix_compatibility(
                analyzed_tracks[i-1]['path'],
                analyzed_tracks[i]['path']
            )
            analyzed_tracks[i]['transition_score'] = compatibility['overall_score']
        
        playlist.append({
            'track': analyzed_tracks[i]['path'],
            'analysis': analyzed_tracks[i]['analysis'],
            'transition_score': analyzed_tracks[i].get('transition_score', 1.0)
        })
    
    return playlist

def generate_waveform(y, sr, output_path):
    plt.figure(figsize=(12, 4))
    plt.plot(np.linspace(0, len(y)/sr, len(y)), y)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def export_analysis_report(track_path, output_format='html'):
    """Generate a detailed analysis report in various formats"""
    analysis = analyze_audio(track_path)
    
    if output_format == 'html':
        report = f"""
        <html>
        <head>
            <title>Track Analysis: {os.path.basename(track_path)}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
                .chart {{ width: 100%; height: 300px; }}
                .mood-radar {{ width: 300px; height: 300px; margin: 20px auto; }}
            </style>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>Track Analysis: {os.path.basename(track_path)}</h1>
            
            <div class="section">
                <h2>Basic Information</h2>
                <p>Tempo: {analysis['tempo']} BPM</p>
                <p>Key: {analysis['key']} (Camelot: {analysis['camelot']})</p>
                <p>Mood: {analysis['mood']['primary_mood']}</p>
                <p>Genre: {analysis['genre']['genre']}</p>
            </div>
            
            <div class="section">
                <h2>Key Changes</h2>
                <p>Number of key changes: {len(analysis['key_changes'])}</p>
                <div id="key-changes-chart" class="chart"></div>
            </div>
            
            <div class="section">
                <h2>Mood Analysis</h2>
                <div id="mood-radar" class="mood-radar"></div>
            </div>
            
            <div class="section">
                <h2>Energy Levels</h2>
                <div id="energy-chart" class="chart"></div>
            </div>
            
            <script>
                // Key changes chart
                var keyChanges = {json.dumps(analysis['key_changes'])};
                var times = keyChanges.map(k => k.time);
                var keys = keyChanges.map(k => k.key);
                
                Plotly.newPlot('key-changes-chart', [{
                    x: times,
                    y: keys,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Key Changes'
                }]);
                
                // Mood radar chart
                var moodScores = {json.dumps(analysis['mood']['mood_scores'])};
                var moodData = [{
                    type: 'scatterpolar',
                    r: Object.values(moodScores),
                    theta: Object.keys(moodScores),
                    fill: 'toself'
                }];
                
                Plotly.newPlot('mood-radar', moodData);
                
                // Energy levels chart
                var energyLevels = {json.dumps(analysis['energy_levels']['segments'])};
                var energyTimes = energyLevels.map(e => e.time);
                var energyValues = energyLevels.map(e => e.energy);
                
                Plotly.newPlot('energy-chart', [{
                    x: energyTimes,
                    y: energyValues,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Energy Level'
                }]);
            </script>
        </body>
        </html>
        """
        
        report_path = f"{track_path}_report.html"
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Open the report in the default browser
        webbrowser.open(f'file://{os.path.abspath(report_path)}')
            
    elif output_format == 'json':
        with open(f"{track_path}_report.json", 'w') as f:
            json.dump(analysis, f, indent=2)

def analyze_audio(audio_path):
    print(f"Analyzing: {audio_path}")
    
    # Load audio for analysis
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    
    # Basic analysis
    tempo = detect_tempo(y, sr)
    key, camelot, confidence = detect_key(audio_path)
    
    # Advanced analysis
    key_changes = detect_key_changes(y, sr)
    mood_analysis = estimate_mood(y, sr)
    beat_grid = analyze_beat_grid(y, sr)
    energy_levels = analyze_energy_levels(y, sr)
    genre = classify_genre(y, sr)
    
    # Generate waveform
    waveform_path = f"{audio_path}_waveform.png"
    generate_waveform(y, sr, waveform_path)
    
    # Get harmonic matches
    harmonic_matches = get_harmonic_matches(camelot)
    
    result = {
        "filename": os.path.basename(audio_path),
        "tempo": round(tempo, 2),
        "key": key,
        "camelot": camelot,
        "confidence": round(confidence, 2),
        "harmonic_matches": harmonic_matches,
        "key_changes": key_changes,
        "mood": mood_analysis,
        "beat_grid": beat_grid,
        "energy_levels": energy_levels,
        "genre": genre,
        "analysis_time": datetime.now().isoformat()
    }
    
    print(f"Estimated Tempo: {result['tempo']} BPM")
    print(f"Estimated Key: {result['key']} (Confidence: {result['confidence']}, Camelot: {result['camelot']})")
    print(f"Primary Mood: {result['mood']['primary_mood']}")
    print(f"Genre: {result['genre']['genre']}")
    print(f"Key Changes: {len(result['key_changes'])} detected")
    
    return result

def process_folder(folder_path):
    results = []
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    
    for file in Path(folder_path).rglob('*'):
        if file.suffix.lower() in audio_extensions:
            try:
                result = analyze_audio(str(file))
                results.append(result)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
    
    return results

def save_results(results, output_dir):
    # Save JSON
    with open(os.path.join(output_dir, 'analysis.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save CSV
    with open(os.path.join(output_dir, 'analysis.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'filename', 'tempo', 'key', 'camelot', 'confidence',
            'primary_mood', 'genre', 'key_changes_count'
        ])
        writer.writeheader()
        for result in results:
            row = {
                'filename': result['filename'],
                'tempo': result['tempo'],
                'key': result['key'],
                'camelot': result['camelot'],
                'confidence': result['confidence'],
                'primary_mood': result['mood']['primary_mood'],
                'genre': result['genre']['genre'],
                'key_changes_count': len(result['key_changes'])
            }
            writer.writerow(row)

def main(path):
    if os.path.isdir(path):
        results = process_folder(path)
        save_results(results, path)
    else:
        analyze_audio(path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audet.py <file.mp3|wav|folder>")
        sys.exit(1)

    path = sys.argv[1]
    main(path)
