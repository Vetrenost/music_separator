import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import torchaudio
import torch

#путь к demucs и модель
DEMUCS_MODEL = "htdemucs"
DEMUCS_EXE = r"C:\Users\Ирина\AppData\Local\Programs\Python\Python312\Scripts\demucs.exe"

def run_demucs(audio_path):
    try:
        result = subprocess.run([DEMUCS_EXE, "-n", DEMUCS_MODEL, audio_path],
                                capture_output=True, text=True)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return str(e)

#объединение дорожек в минусовку
def mix_no_vocals(output_folder):

#пути
    drums = os.path.join(output_folder, "drums.wav")
    bass = os.path.join(output_folder, "bass.wav")
    other = os.path.join(output_folder, "other.wav")
    vocals = os.path.join(output_folder, "vocals.wav")
    no_vocals = os.path.join(output_folder, "no_vocals.wav")

#загрузка дорожек
    d, sr = torchaudio.load(drums)
    b, _ = torchaudio.load(bass)
    o, _ = torchaudio.load(other)

#сложение дорожек
    combined = d + b + o
    combined = combined / combined.abs().max()  # нормализация

    torchaudio.save(no_vocals, combined, sample_rate=sr)

    return vocals, no_vocals

#выбор файлов
def start_separation():
    file_path = filedialog.askopenfilename(
        title="Выберите аудиофайл",
        filetypes=[("Аудиофайлы", "*.mp3 *.wav *.flac *.ogg *.m4a")]
    )
    if not file_path:
        return

    status_label.config(text="Обработка...")
    window.update()

#разделялка
    def worker():
        output = run_demucs(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        model_dir = os.path.join("separated", DEMUCS_MODEL, file_name)

        try:
            vocals_path, no_vocals_path = mix_no_vocals(model_dir)
            messagebox.showinfo("Готово", f"Разделение завершено!\n\n"
                                          f"Вокал: {vocals_path}\n"
                                          f"Минус: {no_vocals_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании no_vocals:\n{str(e)}")

        status_label.config(text="Готово!")
        print(output)

    threading.Thread(target=worker).start()

#кривой интерфейс
window = tk.Tk()
window.title("Demucs — Вокал и Минус")
window.geometry("400x200")
window.resizable(False, False)

tk.Label(window, text="Выбери файл .mp3 .wav .flac .ogg .m4a", font=("Arial", 12)).pack(pady=20)
tk.Button(window, text="Выбрать файл", command=start_separation, font=("Arial", 10)).pack()

status_label = tk.Label(window, text="", fg="blue", font=("Arial", 10))
status_label.pack(pady=20)

window.mainloop()