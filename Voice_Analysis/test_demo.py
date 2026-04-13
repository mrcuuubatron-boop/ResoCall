"""
Тестовый скрипт для Voice Emotion Analyzer
Демонстрирует различные способы использования модуля
"""

import numpy as np
from voice_emotion_analyzer import VoiceEmotionAnalyzer, PsychologicalState
import soundfile as sf
import librosa


def create_test_audio(filename: str, state: str = "calm"):
    """
    Создает тестовое аудио с определенным состоянием.
    
    States:
    - calm: низкий питч, стабильная энергия
    - happy: высокий питч, быстрая речь
    - sad: низкий питч, медленная речь
    - stressed: нестабильный питч, высокая энергия
    - angry: высокий питч, быстро, громко
    """
    
    sr = 16000
    duration = 3  # 3 секунды
    t = np.linspace(0, duration, int(sr * duration))
    
    # Частота основного тона зависит от состояния
    if state == "calm":
        f0 = 120  # Низкий, перепевающий тон
        intensity = 0.3
        vibrato_freq = 0.5  # Медленный вибрато
        
    elif state == "happy":
        f0 = 200  # Высокий тон
        intensity = 0.6
        vibrato_freq = 3.0  # Быстрый вибрато
        
    elif state == "sad":
        f0 = 80  # Очень низкий
        intensity = 0.2
        vibrato_freq = 0.2  # Очень медленный
        
    elif state == "stressed":
        # Нестабильный питч
        f0_base = 150
        f0 = f0_base + 30 * np.sin(2 * np.pi * 2 * t)  # Быстрые колебания
        intensity = 0.5
        vibrato_freq = 4.0
        
    elif state == "angry":
        f0 = 250  # Высокий, острый
        intensity = 0.8
        vibrato_freq = 5.0  # Очень быстрый
        
    else:
        f0 = 130
        intensity = 0.4
        vibrato_freq = 1.0
    
    # Генерируем сигнал (синусоида с вибрато)
    if isinstance(f0, float):
        # Добавляем вибрато для живого звука
        vibrato = 10 * np.sin(2 * np.pi * vibrato_freq * t)
        phase = 2 * np.pi * (f0 + vibrato) * t
    else:
        phase = 2 * np.pi * np.cumsum(f0) / sr
    
    # Основной сигнал
    signal = np.sin(phase) * intensity
    
    # Добавляем огибающую (атака и спад)
    envelope = np.ones_like(t)
    attack_time = 0.1
    attack_samples = int(attack_time * sr)
    release_time = 0.5
    release_samples = int(release_time * sr)
    
    # Attack
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Release
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    signal = signal * envelope
    
    # Добавляем небольшой шум для реалистичности
    noise = np.random.normal(0, 0.05, len(signal))
    signal = signal + noise
    
    # Нормализуем
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.9
    
    # Сохраняем
    sf.write(filename, signal, sr)
        print(f"[OK] Создано тестовое аудио: {filename}")


def demo_basic_usage():
    """Базовая демонстрация использования"""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ 1: Базовое использование")
    print("="*70)
    
    analyzer = VoiceEmotionAnalyzer()
    
    # Анализируем каждое состояние
    states = ["calm", "happy", "sad", "stressed", "angry"]
    
    for state in states:
        # Создаем тестовое аудио
        audio_file = f"test_{state}.wav"
        create_test_audio(audio_file, state)
        
        # Анализируем
        result = analyzer.analyze(audio_file)
        
        print(f"\n📊 Тест: {state.upper()}")
        print(f"   Определено: {result.state.value}")
        print(f"   Уверенность: {result.confidence * 100:.1f}%")
        print(f"   Питч: {result.mean_pitch:.1f} Hz")
        print(f"   Интенсивность: {result.intensity_score:.1f}/10")
        print(f"   Стабильность: {result.stability_score:.1f}/10")
        print(f"   Темп: {result.tempo_score:.1f}/10")


def demo_real_audio():
    """Демонстрация с реальным аудио из ASR папки"""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ 2: Анализ реальных записей из папки test_data")
    print("="*70)
    
    import os
    import glob
    
    analyzer = VoiceEmotionAnalyzer()
    
    # Ищем wav файлы в test_data
    test_files = glob.glob("../test_data/*.wav") + glob.glob("../ASR/*.wav")
    
    if not test_files:
        print("⚠ WAV файлы не найдены в test_data или ASR папке")
        print("  Создайте тестовые записи для анализа")
        return
    
    for audio_file in test_files[:3]:  # Анализируем максимум 3 файла
        try:
            print(f"\n📁 Файл: {os.path.basename(audio_file)}")
            result = analyzer.analyze(audio_file)
            print(f"   Состояние: {result.state.value}")
            print(f"   Уверенность: {result.confidence * 100:.1f}%")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")


def demo_detailed_report():
    """Демонстрация детального отчета"""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ 3: Детальный отчет")
    print("="*70)
    
    analyzer = VoiceEmotionAnalyzer()
    
    # Создаем аудио в состоянии стресса
    audio_file = "test_stressed_demo.wav"
    create_test_audio(audio_file, "stressed")
    
    result = analyzer.analyze(audio_file)
    print(analyzer.get_detailed_report(result))


def demo_batch_analysis():
    """Пакетный анализ нескольких файлов"""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ 4: Пакетный анализ")
    print("="*70)
    
    analyzer = VoiceEmotionAnalyzer()
    
    print("\nСоздаю тестовые файлы...")
    test_files = []
    for state in ["calm", "happy", "sad", "stressed", "angry"]:
        audio_file = f"batch_test_{state}.wav"
        create_test_audio(audio_file, state)
        test_files.append(audio_file)
    
    print("\nРезультаты пакетного анализа:")
    print("-" * 70)
    print(f"{'Файл':<30} {'Состояние':<15} {'Уверенность':<15}")
    print("-" * 70)
    
    results = []
    for audio_file in test_files:
        result = analyzer.analyze(audio_file)
        results.append(result)
        print(f"{audio_file:<30} {result.state.value:<15} {result.confidence*100:>6.1f}%")
    
    # Статистика
    print("-" * 70)
    avg_confidence = np.mean([r.confidence for r in results])
    print(f"Средняя уверенность: {avg_confidence*100:.1f}%")
    
    # Распределение состояний
    state_counts = {}
    for result in results:
        state_counts[result.state.value] = state_counts.get(result.state.value, 0) + 1
    
    print("\nРаспределение состояний:")
    for state, count in state_counts.items():
        print(f"  {state}: {count} запись(ей)")


def cleanup_test_files():
    """Удаляет тестовые файлы"""
    import os
    import glob
    
    test_files = glob.glob("test_*.wav") + glob.glob("batch_test_*.wav")
    for f in test_files:
        try:
            os.remove(f)
            print(f"Удален: {f}")
        except:
            pass


if __name__ == "__main__":
    print("\n" + "[VA] " * 35)
    print("VOICE EMOTION ANALYZER - ТЕСТИРОВАНИЕ")
    print("[VA] " * 35)
    
    # Запускаем демонстрации
    try:
        demo_basic_usage()
        demo_detailed_report()
        demo_batch_analysis()
        
        # Опциональный демо с реальным аудио
        # demo_real_audio()
        
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Очищаем тестовые файлы
        print("\n" + "="*70)
        print("Очистка тестовых файлов...")
        cleanup_test_files()
        print("Готово!")
