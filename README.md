Помести файл скрипта main.py в удобное место
Рядом с ним должен находиться файл demucs.exe
Не советую менять модель в коде

Требования
Python 3.12+
torchaudio
demucs.exe 
ffmpeg - скачать ffmpeg-release-essentials с сайта https://www.gyan.dev/ffmpeg/builds/ разархивировать в папку с main.py


В открывшемся окне:
Нажми кнопку «Выбрать файл»
Выбери аудиофайл (.mp3, .wav, .flac, .ogg, .m4a)
На обработку может понадобиться больше минуты
Результаты появятся в папке separated/htdemucs/название_трека/ рядом со скриптом:
vocals.wav — вокал
no_vocals.wav — минусовка

