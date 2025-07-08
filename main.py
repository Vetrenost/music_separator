import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import threading
import torchaudio
from pydub import AudioSegment
from pydub.utils import which

# определение пути до скрипта
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# путь к ffmpeg. Держать в одной папке с main.py
FFMPEG_PATH = os.path.join(APP_DIR, "ffmpeg", "bin", "ffmpeg.exe") 
AudioSegment.converter = FFMPEG_PATH

# путь к demucs. Тоже держать в одной папке с main.py
DEMUCS_EXE = os.path.join(APP_DIR, "demucs.exe")

# поддерживаемые форматы
EXPORT_FORMATS = ["wav", "mp3", "flac"]

# запуск demucs
def run_demucs(audio_path, model_name="htdemucs"):
    try:
        result = subprocess.run(
            [DEMUCS_EXE, "-n", model_name, audio_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout + "\n" + result.stderr
    except subprocess.CalledProcessError as e:
        return f"Demucs error:\n{e.stdout}\n{e.stderr}"
    except Exception as e:
        return str(e)

# смешивание дорожек без вокала, 
def mix_no_vocals(output_folder, output_name, export_format):
    drums = os.path.join(output_folder, "drums.wav")
    bass = os.path.join(output_folder, "bass.wav")
    other = os.path.join(output_folder, "other.wav")
    vocals = os.path.join(output_folder, "vocals.wav")

    # пути до выходных файлов
    no_vocals_out = os.path.join(APP_DIR, f"{output_name}_no_vocals.{export_format}")
    vocals_out = os.path.join(APP_DIR, f"{output_name}_vocals.{export_format}")

    d, sr = torchaudio.load(drums)
    b, _ = torchaudio.load(bass)
    o, _ = torchaudio.load(other)
    v, _ = torchaudio.load(vocals)

    minus = d + b + o
    minus = minus / minus.abs().max()

    temp_minus = os.path.join(APP_DIR, "_temp_minus.wav")
    temp_vocals = os.path.join(APP_DIR, "_temp_vocals.wav")

    torchaudio.save(temp_minus, minus, sample_rate=sr)
    torchaudio.save(temp_vocals, v, sample_rate=sr)

    AudioSegment.from_wav(temp_minus).export(no_vocals_out, format=export_format)
    AudioSegment.from_wav(temp_vocals).export(vocals_out, format=export_format)

    os.remove(temp_minus)
    os.remove(temp_vocals)

    return vocals_out, no_vocals_out

# обработка файла
def start_separation():
    file_path = filedialog.askopenfilename(
        title="Выберите аудиофайл",
        filetypes=[("Аудиофайлы", "*.mp3 *.wav *.flac *.ogg *.m4a")]
    )
    if not file_path:
        return

    export_format = format_var.get()
    if export_format not in EXPORT_FORMATS:
        messagebox.showerror("Ошибка", "Выбран неподдерживаемый формат")
        return

    status_label.config(text="Обработка...")
    window.update()

    def worker():
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            output = run_demucs(file_path)
            model_dir = os.path.join(APP_DIR, "separated", "htdemucs", file_name)
            vocals_path, no_vocals_path = mix_no_vocals(model_dir, file_name, export_format)
            messagebox.showinfo("Готово", f"Вокал: {vocals_path}\nМинус: {no_vocals_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        status_label.config(text="Готово!")

    threading.Thread(target=worker).start()

# кривой интерфейс
window = tk.Tk()
window.title("Demucs — Минусатор")
window.geometry("420x220")
window.resizable(False, False)

# выбор файла
tk.Label(window, text="Выберите аудиофайл", font=("Arial", 12)).pack(pady=10)
tk.Button(window, text="Обработать", command=start_separation, font=("Arial", 11)).pack(pady=10)

# выбор формата файла на выходе
tk.Label(window, text="Формат выхода:", font=("Arial", 10)).pack()
format_var = tk.StringVar(value=EXPORT_FORMATS[0])
tk.OptionMenu(window, format_var, *EXPORT_FORMATS).pack()

status_label = tk.Label(window, text="", fg="blue", font=("Arial", 10))
status_label.pack(pady=10)

window.mainloop()
