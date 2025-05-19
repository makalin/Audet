import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import queue
import os
from pathlib import Path
import audet
import webbrowser

class AudetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 Audet — Audio Intelligence")
        self.root.geometry("1000x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TFrame", background="#f0f0f0")
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Analysis tab
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Analysis")
        
        # Playlist tab
        self.playlist_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.playlist_tab, text="Playlist Generator")
        
        # Mix Compatibility tab
        self.mix_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mix_tab, text="Mix Compatibility")
        
        self.setup_analysis_tab()
        self.setup_playlist_tab()
        self.setup_mix_tab()
        
        # Queue for thread communication
        self.queue = queue.Queue()
    
    def setup_analysis_tab(self):
        # Drop zone
        self.drop_frame = ttk.LabelFrame(self.analysis_tab, text="Drop Audio Files Here", padding="20")
        self.drop_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.drop_label = ttk.Label(
            self.drop_frame,
            text="Drag and drop audio files or folders here\nSupported formats: MP3, WAV, FLAC, OGG, M4A",
            justify=tk.CENTER
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
        # Configure drag and drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Progress section
        self.progress_frame = ttk.LabelFrame(self.analysis_tab, text="Progress", padding="10")
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.pack(fill=tk.X)
        
        # Results section
        self.results_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create Treeview for results
        self.tree = ttk.Treeview(
            self.results_frame,
            columns=("filename", "tempo", "key", "camelot", "mood", "genre", "confidence"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("filename", text="Filename")
        self.tree.heading("tempo", text="BPM")
        self.tree.heading("key", text="Key")
        self.tree.heading("camelot", text="Camelot")
        self.tree.heading("mood", text="Mood")
        self.tree.heading("genre", text="Genre")
        self.tree.heading("confidence", text="Confidence")
        
        self.tree.column("filename", width=200)
        self.tree.column("tempo", width=80)
        self.tree.column("key", width=100)
        self.tree.column("camelot", width=80)
        self.tree.column("mood", width=100)
        self.tree.column("genre", width=100)
        self.tree.column("confidence", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        self.button_frame = ttk.Frame(self.analysis_tab)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            self.button_frame,
            text="Export Report",
            command=self.export_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.button_frame,
            text="Show Details",
            command=self.show_details
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.show_harmonic_matches)
    
    def setup_playlist_tab(self):
        # Target mood selection
        mood_frame = ttk.LabelFrame(self.playlist_tab, text="Target Mood", padding="10")
        mood_frame.pack(fill=tk.X, pady=10)
        
        self.mood_var = tk.StringVar(value="energetic")
        for mood in audet.MOODS.keys():
            ttk.Radiobutton(
                mood_frame,
                text=mood.capitalize(),
                value=mood,
                variable=self.mood_var
            ).pack(side=tk.LEFT, padx=10)
        
        # File selection
        file_frame = ttk.LabelFrame(self.playlist_tab, text="Select Tracks", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.playlist_tree = ttk.Treeview(
            file_frame,
            columns=("filename",),
            show="headings"
        )
        self.playlist_tree.heading("filename", text="Filename")
        self.playlist_tree.column("filename", width=400)
        
        playlist_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_scrollbar.set)
        
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(self.playlist_tab)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Add Files",
            command=self.add_playlist_files
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Generate Playlist",
            command=self.generate_playlist
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_playlist
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_mix_tab(self):
        # Track selection
        selection_frame = ttk.Frame(self.mix_tab)
        selection_frame.pack(fill=tk.X, pady=10)
        
        # Track 1
        track1_frame = ttk.LabelFrame(selection_frame, text="Track 1", padding="10")
        track1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.track1_var = tk.StringVar()
        ttk.Entry(
            track1_frame,
            textvariable=self.track1_var,
            state="readonly"
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            track1_frame,
            text="Browse",
            command=lambda: self.browse_track(1)
        ).pack(fill=tk.X)
        
        # Track 2
        track2_frame = ttk.LabelFrame(selection_frame, text="Track 2", padding="10")
        track2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.track2_var = tk.StringVar()
        ttk.Entry(
            track2_frame,
            textvariable=self.track2_var,
            state="readonly"
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            track2_frame,
            text="Browse",
            command=lambda: self.browse_track(2)
        ).pack(fill=tk.X)
        
        # Analysis button
        ttk.Button(
            self.mix_tab,
            text="Analyze Compatibility",
            command=self.analyze_compatibility
        ).pack(pady=10)
        
        # Results
        self.mix_results = ttk.LabelFrame(self.mix_tab, text="Compatibility Results", padding="10")
        self.mix_results.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.mix_text = tk.Text(self.mix_results, height=10, wrap=tk.WORD)
        self.mix_text.pack(fill=tk.BOTH, expand=True)
    
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if not files:
            return
            
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_files, args=(files,))
        thread.daemon = True
        thread.start()
        
        # Start checking the queue
        self.check_queue()
    
    def process_files(self, files):
        total_files = len(files)
        processed = 0
        
        for file in files:
            try:
                if os.path.isdir(file):
                    results = audet.process_folder(file)
                    for result in results:
                        self.queue.put(("result", result))
                else:
                    result = audet.analyze_audio(file)
                    self.queue.put(("result", result))
                
                processed += 1
                self.queue.put(("progress", (processed / total_files) * 100))
                
            except Exception as e:
                self.queue.put(("error", f"Error processing {file}: {str(e)}"))
        
        self.queue.put(("done", None))
    
    def check_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == "result":
                    self.tree.insert("", tk.END, values=(
                        data["filename"],
                        f"{data['tempo']:.1f}",
                        data["key"],
                        data["camelot"],
                        data["mood"]["primary_mood"],
                        data["genre"]["genre"],
                        f"{data['confidence']:.2f}"
                    ))
                elif msg_type == "progress":
                    self.progress_var.set(data)
                    self.status_label.config(text=f"Processing... {data:.1f}%")
                elif msg_type == "error":
                    messagebox.showerror("Error", data)
                elif msg_type == "done":
                    self.status_label.config(text="Analysis complete!")
                    self.progress_var.set(100)
                
                self.queue.task_done()
                
        except queue.Empty:
            self.root.after(100, self.check_queue)
    
    def show_harmonic_matches(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item)["values"]
        filename = values[0]
        
        # Find the result in the tree
        for result in self.tree.get_children():
            if self.tree.item(result)["values"][0] == filename:
                camelot = self.tree.item(result)["values"][3]
                matches = audet.get_harmonic_matches(camelot)
                
                # Show matches in a new window
                match_window = tk.Toplevel(self.root)
                match_window.title(f"Harmonic Matches for {filename}")
                match_window.geometry("300x200")
                
                ttk.Label(
                    match_window,
                    text=f"Compatible keys for {camelot}:",
                    padding=10
                ).pack()
                
                for match in matches:
                    ttk.Label(
                        match_window,
                        text=match,
                        padding=5
                    ).pack()
                
                break
    
    def export_report(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a track to export")
            return
        
        item = selection[0]
        filename = self.tree.item(item)["values"][0]
        
        # Find the full path
        for result in self.tree.get_children():
            if self.tree.item(result)["values"][0] == filename:
                track_path = os.path.join(os.getcwd(), filename)
                audet.export_analysis_report(track_path)
                break
    
    def show_details(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a track to view details")
            return
        
        item = selection[0]
        filename = self.tree.item(item)["values"][0]
        
        # Find the full path and analysis
        for result in self.tree.get_children():
            if self.tree.item(result)["values"][0] == filename:
                track_path = os.path.join(os.getcwd(), filename)
                analysis = audet.analyze_audio(track_path)
                
                # Show details in a new window
                details_window = tk.Toplevel(self.root)
                details_window.title(f"Track Details: {filename}")
                details_window.geometry("600x400")
                
                # Create text widget with scrollbar
                text_frame = ttk.Frame(details_window)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text = tk.Text(text_frame, wrap=tk.WORD)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
                text.configure(yscrollcommand=scrollbar.set)
                
                text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Format and display analysis
                text.insert(tk.END, f"Track: {filename}\n\n")
                text.insert(tk.END, f"Tempo: {analysis['tempo']} BPM\n")
                text.insert(tk.END, f"Key: {analysis['key']} (Camelot: {analysis['camelot']})\n")
                text.insert(tk.END, f"Mood: {analysis['mood']['primary_mood']}\n")
                text.insert(tk.END, f"Genre: {analysis['genre']['genre']}\n\n")
                
                text.insert(tk.END, "Mood Scores:\n")
                for mood, score in analysis['mood']['mood_scores'].items():
                    text.insert(tk.END, f"- {mood}: {score:.2f}\n")
                
                text.insert(tk.END, "\nKey Changes:\n")
                for change in analysis['key_changes']:
                    text.insert(tk.END, f"- {change['time']:.1f}s: {change['key']} ({change['camelot']})\n")
                
                text.insert(tk.END, "\nEnergy Analysis:\n")
                text.insert(tk.END, f"- Average Energy: {analysis['energy_levels']['average_energy']:.2f}\n")
                text.insert(tk.END, f"- Energy Variance: {analysis['energy_levels']['energy_variance']:.2f}\n")
                
                text.configure(state="disabled")
                break
    
    def add_playlist_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
                ("All Files", "*.*")
            ]
        )
        
        for file in files:
            self.playlist_tree.insert("", tk.END, values=(file,))
    
    def generate_playlist(self):
        files = [self.playlist_tree.item(item)["values"][0] for item in self.playlist_tree.get_children()]
        if not files:
            messagebox.showwarning("Warning", "Please add files to the playlist")
            return
        
        target_mood = self.mood_var.get()
        playlist = audet.generate_playlist(files, target_mood)
        
        # Show playlist in a new window
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title("Generated Playlist")
        playlist_window.geometry("600x400")
        
        # Create treeview
        tree = ttk.Treeview(
            playlist_window,
            columns=("track", "tempo", "key", "mood", "transition"),
            show="headings"
        )
        
        tree.heading("track", text="Track")
        tree.heading("tempo", text="BPM")
        tree.heading("key", text="Key")
        tree.heading("mood", text="Mood")
        tree.heading("transition", text="Transition Score")
        
        tree.column("track", width=300)
        tree.column("tempo", width=80)
        tree.column("key", width=100)
        tree.column("mood", width=100)
        tree.column("transition", width=100)
        
        for item in playlist:
            tree.insert("", tk.END, values=(
                os.path.basename(item['track']),
                f"{item['analysis']['tempo']:.1f}",
                item['analysis']['camelot'],
                item['analysis']['mood']['primary_mood'],
                f"{item['transition_score']:.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def clear_playlist(self):
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
    
    def browse_track(self, track_num):
        file = filedialog.askopenfilename(
            title=f"Select Track {track_num}",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
                ("All Files", "*.*")
            ]
        )
        
        if file:
            if track_num == 1:
                self.track1_var.set(file)
            else:
                self.track2_var.set(file)
    
    def analyze_compatibility(self):
        track1 = self.track1_var.get()
        track2 = self.track2_var.get()
        
        if not track1 or not track2:
            messagebox.showwarning("Warning", "Please select both tracks")
            return
        
        try:
            compatibility = audet.analyze_mix_compatibility(track1, track2)
            
            # Update results
            self.mix_text.delete(1.0, tk.END)
            self.mix_text.insert(tk.END, f"Mix Compatibility Analysis:\n\n")
            self.mix_text.insert(tk.END, f"Tempo Compatibility: {compatibility['tempo_compatibility']:.2f}\n")
            self.mix_text.insert(tk.END, f"Key Compatibility: {'Yes' if compatibility['key_compatibility'] else 'No'}\n")
            self.mix_text.insert(tk.END, f"Energy Compatibility: {compatibility['energy_compatibility']:.2f}\n")
            self.mix_text.insert(tk.END, f"\nOverall Score: {compatibility['overall_score']:.2f}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing compatibility: {str(e)}")

def main():
    root = TkinterDnD.Tk()
    app = AudetGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 