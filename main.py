import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import threading
import torchaudio

# определение папки
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# путь к demucs
DEMUCS_EXE = os.path.join(APP_DIR, "demucs.exe")  # demucs держать в одной папке с этим файлом

# запуск demucs и вывод ошибок
def run_demucs(audio_path, model_name="htdemucs"):
    try:
        result = subprocess.run([DEMUCS_EXE, "-n", model_name, audio_path], capture_output=True, text=True, check=True)
        return result.stdout + "\n" + result.stderr
    except subprocess.CalledProcessError as e:
        return f"Demucs error:\n{e.stdout}\n{e.stderr}"
    except Exception as e:
        return str(e)

# смешивание дорожек для минусовки
def mix_no_vocals(output_folder, output_name):
    drums = os.path.join(output_folder, "drums.wav")
    bass = os.path.join(output_folder, "bass.wav")
    other = os.path.join(output_folder, "other.wav")
    vocals = os.path.join(output_folder, "vocals.wav")

    no_vocals = os.path.join(APP_DIR, f"{output_name}_no_vocals.wav")
    vocals_out = os.path.join(APP_DIR, f"{output_name}_vocals.wav")

    d, sr = torchaudio.load(drums)
    b, _ = torchaudio.load(bass)
    o, _ = torchaudio.load(other)
    v, _ = torchaudio.load(vocals)

    combined = d + b + o
    combined = combined / combined.abs().max() 

    torchaudio.save(no_vocals, combined, sample_rate=sr)
    torchaudio.save(vocals_out, v, sample_rate=sr)

    return vocals_out, no_vocals

# обработка файла
def start_separation():
    file_path = filedialog.askopenfilename(
        title="Выберите аудиофайл",
        filetypes=[("Аудиофайлы", "*.mp3 *.wav *.flac *.ogg *.m4a")]
    )
    if not file_path:
        return

    status_label.config(text="Обработка...")
    window.update()

    def worker():
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            output = run_demucs(file_path)
            model_dir = os.path.join(APP_DIR, "separated", "htdemucs", file_name) # модель не менять, всё сломается

            vocals_path, no_vocals_path = mix_no_vocals(model_dir, file_name)
            messagebox.showinfo("Готово", f"Вокал: {vocals_path}\nМинус: {no_vocals_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        status_label.config(text="Готово!")

    threading.Thread(target=worker).start()

# кривой интерфейс
window = tk.Tk()
window.title("Минусатор")
window.geometry("400x200")
window.resizable(False, False)

tk.Label(window, text="Выберите аудиофайл", font=("Arial", 12)).pack(pady=20)
tk.Button(window, text="Обработать", command=start_separation, font=("Arial", 10)).pack()

status_label = tk.Label(window, text="", fg="blue", font=("Arial", 10))
status_label.pack(pady=20)

window.mainloop()
