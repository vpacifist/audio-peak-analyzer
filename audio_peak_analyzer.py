import os
from tkinter import Tk, filedialog, Label, Button, Text, Scrollbar, RIGHT, Y, END
from pydub import AudioSegment
import numpy as np
import ffmpeg

# Устанавливаем путь к ffmpeg
ffmpeg_path = r"C:\Program Files\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"

# Устанавливаем путь для pydub
AudioSegment.converter = ffmpeg_path

# Добавляем путь в переменные окружения (на всякий случай)
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# Проверка работы ffmpeg
try:
    # Проверка работы ffmpeg - просто проверяем версию без использования реального файла
    ffmpeg.probe(ffmpeg_path)
except ffmpeg.Error as e:
    print('FFmpeg error:', e)

class AudioPeakAnalyzer:
    def __init__(self, master):
        self.master = master
        master.title("Audio Peak Analyzer")

        self.label = Label(master, text="Выберите аудиофайлы для анализа.")
        self.label.pack()

        self.analyze_button = Button(master, text="Анализировать", command=self.analyze)
        self.analyze_button.pack()

        self.result_text = Text(master, wrap='word', height=15, width=60)
        self.result_text.pack()

        self.scrollbar = Scrollbar(master, command=self.result_text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

         # Привязываем сочетание клавиш Ctrl+C к методу copy_selected_text
        master.bind('<Control-c>', self.copy_selected_text)

    def analyze(self):
        # Открываем диалоговое окно для выбора нескольких файлов
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg")])

        if not file_paths:
            return  # Если файлы не выбраны, выходим

        # Очищаем текстовое поле с результатами
        self.result_text.delete(1.0, END)
        
        # Проходим по каждому выбранному файлу и выполняем анализ
        for file_path in file_paths:
            try:
                # Загружаем аудиофайл с помощью pydub
                audio = AudioSegment.from_file(file_path)
                samples = np.array(audio.get_array_of_samples())

                # Для стерео разделяем каналы и находим максимальное значение в обоих каналах
                if audio.channels == 2:
                    left_channel = samples[::2]  # Чётные индексы - левый канал
                    right_channel = samples[1::2]  # Нечётные индексы - правый канал
                    combined_samples = np.maximum(np.abs(left_channel), np.abs(right_channel))
                else:
                    combined_samples = np.abs(samples)

                # Находим абсолютное значение всех сэмплов для поиска пика
                peak_value = np.max(combined_samples)
                peak_index = np.argmax(combined_samples)

                # Расчёт времени, когда произошёл пик
                duration_seconds = len(audio) / 1000.0  # Длительность трека в секундах
                sample_rate = audio.frame_rate

                # Перевод индекса пикового сэмпла во время (секунды)
                peak_time = peak_index / sample_rate

                # Проверка, что рассчитанное время пика не выходит за пределы длительности трека
                if peak_time > duration_seconds:
                    peak_time = duration_seconds

                # Преобразуем значение пика в дБ
                peak_db = 20 * np.log10(peak_value / (2**(audio.sample_width * 8 - 1)))

                # Добавляем результаты в текстовое поле
                self.result_text.insert(END, f"File: {os.path.basename(file_path)}\n")
                self.result_text.insert(END, f"Max Peak: {peak_db:.2f} dB at {peak_time:.2f} seconds\n")
                self.result_text.insert(END, "\n")

            except Exception as e:
                self.result_text.insert(END, f"File: {os.path.basename(file_path)}\n")
                self.result_text.insert(END, f"Ошибка: {str(e)}\n\n")

# Запуск интерфейса
root = Tk()
audio_peak_analyzer = AudioPeakAnalyzer(root)
root.mainloop()