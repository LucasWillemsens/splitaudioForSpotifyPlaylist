import sys
import threading
import argparse

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    TK_AVAILABLE = True
except ModuleNotFoundError:
    tk = None
    filedialog = None
    messagebox = None
    scrolledtext = None
    TK_AVAILABLE = False

try:
    from .cli import run_split
except (ImportError, ValueError):
    from cli import run_split


if TK_AVAILABLE:
    class TextRedirector:
        def __init__(self, text_widget, tag="stdout"):
            self.text_widget = text_widget
            self.tag = tag

        def write(self, string):
            self.text_widget.after(0, lambda: self._do_write(string))

        def _do_write(self, string):
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, string, (self.tag,))
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")

        def flush(self):
            pass


    class SplitAudioGui:
        def __init__(self, master):
            self.master = master
            master.title("Split Audio")
            master.geometry("800x700")

            try:
                photo = tk.PhotoImage(file="app.png")
                master.iconphoto(False, photo)
            except tk.TclError:
                pass

            # Set minimum size
            master.minsize(600, 500)

            # Main frame
            main_frame = tk.Frame(master, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Fields frame
            fields_frame = tk.LabelFrame(main_frame, text="Settings", padx=15, pady=15)
            fields_frame.pack(fill=tk.X, pady=10)

            row = 0

            # Audio File
            tk.Label(fields_frame, text="Audio File:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.audio_file_var = tk.StringVar()
            self.audio_file_entry = tk.Entry(fields_frame, textvariable=self.audio_file_var, width=50)
            self.audio_file_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            tk.Button(fields_frame, text="Browse...", command=self.browse_audio).grid(row=row, column=2, padx=5, pady=5)
            row += 1

            # CSV File
            tk.Label(fields_frame, text="CSV File:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.csv_file_var = tk.StringVar()
            self.csv_file_entry = tk.Entry(fields_frame, textvariable=self.csv_file_var, width=50)
            self.csv_file_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            tk.Button(fields_frame, text="Browse...", command=self.browse_csv).grid(row=row, column=2, padx=5, pady=5)
            row += 1

            # Output Path
            tk.Label(fields_frame, text="Output Path:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.output_path_var = tk.StringVar()
            self.output_path_entry = tk.Entry(fields_frame, textvariable=self.output_path_var, width=50)
            self.output_path_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            tk.Button(fields_frame, text="Browse...", command=self.browse_output).grid(row=row, column=2, padx=5, pady=5)
            row += 1

            # Artist
            tk.Label(fields_frame, text="Artist:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.artist_var = tk.StringVar()
            tk.Entry(fields_frame, textvariable=self.artist_var, width=50).grid(
                row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew"
            )
            row += 1

            # Album
            tk.Label(fields_frame, text="Album:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.album_var = tk.StringVar()
            tk.Entry(fields_frame, textvariable=self.album_var, width=50).grid(
                row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew"
            )
            row += 1

            # Year
            tk.Label(fields_frame, text="Year:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            self.year_var = tk.StringVar()
            tk.Entry(fields_frame, textvariable=self.year_var, width=50).grid(
                row=row, column=1, columnspan=2, padx=5, pady=5, sticky="ew"
            )
            row += 1

            # Options frame
            options_frame = tk.Frame(fields_frame)
            options_frame.grid(row=row, column=1, sticky="w", pady=5)

            # Dry Run
            self.dry_run_var = tk.BooleanVar()
            tk.Checkbutton(options_frame, text="Dry Run (simulation only)", variable=self.dry_run_var).pack(side=tk.LEFT)
            row += 1

            fields_frame.columnconfigure(1, weight=1)

            # Action Button
            self.process_button = tk.Button(
                main_frame,
                text="Start Processing",
                command=self.process,
                height=2,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 11, "bold"),
            )
            self.process_button.pack(fill=tk.X, pady=15)

            # Output frame
            output_frame = tk.LabelFrame(main_frame, text="Console Output", padx=10, pady=10)
            output_frame.pack(fill=tk.BOTH, expand=True)

            self.output_text = scrolledtext.ScrolledText(output_frame, height=12, state="disabled", font=("Courier", 10))
            self.output_text.pack(fill=tk.BOTH, expand=True)
            self.output_text.tag_config("stderr", foreground="red")

        def browse_audio(self):
            filetypes = [
                ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                ("All files", "*.*"),
            ]
            filename = filedialog.askopenfilename(title="Select Audio File", filetypes=filetypes)
            if filename:
                self.audio_file_var.set(filename)

        def browse_csv(self):
            filetypes = [
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ]
            filename = filedialog.askopenfilename(title="Select CSV File", filetypes=filetypes)
            if filename:
                self.csv_file_var.set(filename)

        def browse_output(self):
            directory = filedialog.askdirectory(title="Select Output Directory")
            if directory:
                self.output_path_var.set(directory)

        def process(self):
            input_file = self.audio_file_var.get().strip()
            csv_file = self.csv_file_var.get().strip()
            output_path = self.output_path_var.get().strip()
            artist = self.artist_var.get().strip() or None
            album = self.album_var.get().strip() or None
            year = self.year_var.get().strip()
            dry_run = self.dry_run_var.get()

            if not input_file or not csv_file:
                messagebox.showerror("Error", "Input audio file and CSV file are required.")
                return

            try:
                if year:
                    year_val = int(year)
                else:
                    year_val = None
            except ValueError:
                messagebox.showerror("Error", "Year must be an integer.")
                return

            self.process_button.configure(state="disabled")
            self.output_text.configure(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.configure(state="disabled")

            # Run in a thread to keep GUI responsive
            thread = threading.Thread(
                target=self.run_process,
                args=(input_file, csv_file, output_path, artist, album, year_val, dry_run),
                daemon=True,
            )
            thread.start()

        def run_process(self, input_file, csv_file, output_path, artist, album, year, dry_run):
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = TextRedirector(self.output_text, "stdout")
            sys.stderr = TextRedirector(self.output_text, "stderr")

            try:
                run_split(input_file, csv_file, output_path, artist, album, year, dry_run)
                self.master.after(0, lambda: messagebox.showinfo("Success", "Processing completed."))
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                self.master.after(0, lambda: self.process_button.configure(state="normal"))


def _run_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="splitaudio-gui2",
        description="Splitaudio GUI (Tkinter) with CLI fallback when Tkinter isn't available.",
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the source audio file.")
    parser.add_argument("-c", "--csv", required=True, help="Path to the CSV cue list.")
    parser.add_argument("-o", "--output", default="", help="Output directory. Default: input file's parent.")
    parser.add_argument("-r", "--artist", default=None, help="Default artist (used if CSV row doesn't override).")
    parser.add_argument("-a", "--album", default=None, help="Default album (used if CSV row doesn't override).")
    parser.add_argument("-y", "--year", type=int, default=None, help="Default year (used if CSV row doesn't override).")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Simulate only; don't write files.")

    args = parser.parse_args(argv)

    # Match the GUI's behavior: empty output means "let run_split decide default"
    output_path = args.output.strip() or None

    run_split(
        args.input,
        args.csv,
        output_path,
        args.artist,
        args.album,
        args.year,
        args.dry_run,
    )
    return 0


def main():
    if TK_AVAILABLE:
        root = tk.Tk()
        gui = SplitAudioGui(root)
        root.mainloop()
        return

    print(
        "Tkinter is not available in this Python environment, so the GUI cannot be started.\n"
        "Falling back to CLI mode.\n\n"
        "Example:\n"
        "  python -m splitaudio.gui2 --input <PATH_TO_AUDIO> --csv <PATH_TO_CSV> --output <OUT_DIR>\n",
        file=sys.stderr,
    )
    raise SystemExit(_run_cli(sys.argv[1:]))


if __name__ == "__main__":
    main()
