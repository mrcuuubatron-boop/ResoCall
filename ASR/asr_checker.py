#!/usr/bin/env python3
"""
ASR Quality Checker - оценка качества транскрибации с сохранением отчета
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def get_file_from_user(prompt, extension=".txt"):
    """Интерактивный выбор файла"""
    while True:
        print(f"\n📁 {prompt}")
        file_path = input("Введите путь к файлу (или нажмите Enter для выбора из текущей папки): ").strip()
        
        if not file_path:
            # Показываем файлы в текущей папке
            files = [f for f in os.listdir('.') if f.endswith(extension)]
            if not files:
                print(f"❌ Нет файлов с расширением {extension} в текущей папке")
                continue
            
            print(f"\nДоступные файлы:")
            for i, f in enumerate(files, 1):
                print(f"  {i}. {f}")
            
            choice = input(f"\nВыберите номер файла (1-{len(files)}) или введите путь: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(files):
                file_path = files[int(choice)-1]
            else:
                file_path = choice
        
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"❌ Файл '{file_path}' не найден. Попробуйте снова.")

def load_hypothesis(file_path):
    """Загружает гипотезу из файла: если JSON с segments, извлекает текст; иначе читает построчно."""
    if file_path.lower().endswith('.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'segments' in data and isinstance(data['segments'], list):
                # Извлекаем текст из каждого сегмента, убираем пустые строки
                lines = [seg.get('text', '').strip() for seg in data['segments'] if seg.get('text', '').strip()]
                return lines
            else:
                # Если нет segments, пробуем взять весь текст как одну строку
                if 'text' in data:
                    return [data['text'].strip()]
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️ Не удалось прочитать JSON, пробуем как текст: {e}")
    # Если не JSON или не получилось, читаем как обычный текст построчно
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines

def calculate_wer(ref_text, hyp_text):
    """Расчет WER (Word Error Rate)"""
    ref_words = ref_text.split()
    hyp_words = hyp_text.split()
    
    # Простая матрица расстояния Левенштейна для слов
    n, m = len(ref_words), len(hyp_words)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    return dp[n][m], n

def calculate_cer(ref_text, hyp_text):
    """Расчет CER (Character Error Rate)"""
    ref_chars = list(ref_text)
    hyp_chars = list(hyp_text)
    
    n, m = len(ref_chars), len(hyp_chars)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    return dp[n][m], n

def align_words(ref_words, hyp_words):
    """Выравнивание слов для поиска ошибок"""
    n, m = len(ref_words), len(hyp_words)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    # Восстановление пути
    i, j = n, m
    subs, dels, ins = [], [], []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i-1] == hyp_words[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            subs.append((ref_words[i-1], hyp_words[j-1]))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            dels.append(ref_words[i-1])
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            ins.append(hyp_words[j-1])
            j -= 1
        else:
            break
    
    return subs[::-1], dels[::-1], ins[::-1]

def generate_report(ref_file, hyp_file, output_file=None):
    """Генерация полного отчета"""
    
    # Читаем эталон (обычный текстовый файл)
    with open(ref_file, 'r', encoding='utf-8') as f:
        ref_lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Читаем гипотезу (может быть JSON или текст)
    hyp_lines = load_hypothesis(hyp_file)
    
    # Выравниваем количество строк
    if len(ref_lines) != len(hyp_lines):
        print(f"⚠️ Предупреждение: эталонов {len(ref_lines)}, гипотез {len(hyp_lines)}")
        min_len = min(len(ref_lines), len(hyp_lines))
        ref_lines = ref_lines[:min_len]
        hyp_lines = hyp_lines[:min_len]
    
    # Создаем имя выходного файла
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"asr_report_{timestamp}.txt"
    
    # Генерируем отчет
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write("📊 ОТЧЕТ ОЦЕНКИ КАЧЕСТВА ТРАНСКРИБАЦИИ ASR\n")
        out.write("=" * 80 + "\n")
        out.write(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"📁 Эталонный файл: {ref_file}\n")
        out.write(f"📁 Проверяемый файл: {hyp_file}\n")
        out.write("=" * 80 + "\n\n")
        
        total_wer = 0
        total_cer = 0
        sentences_with_errors = 0
        all_subs, all_dels, all_ins = [], [], []
        
        # Построчная оценка
        for i, (ref, hyp) in enumerate(zip(ref_lines, hyp_lines), 1):
            wer_dist, wer_len = calculate_wer(ref, hyp)
            wer = wer_dist / wer_len if wer_len > 0 else 0
            
            cer_dist, cer_len = calculate_cer(ref, hyp)
            cer = cer_dist / cer_len if cer_len > 0 else 0
            
            total_wer += wer
            total_cer += cer
            
            if wer > 0:
                sentences_with_errors += 1
            
            out.write(f"{'─' * 80}\n")
            out.write(f"📝 ПРЕДЛОЖЕНИЕ {i}\n")
            out.write(f"{'─' * 80}\n")
            out.write(f"✅ ЭТАЛОН:    {ref}\n")
            out.write(f"❓ ГИПОТЕЗА:  {hyp}\n")
            out.write(f"\n📈 МЕТРИКИ:\n")
            out.write(f"   • WER (Word Error Rate): {wer:.2%} ({wer_dist}/{wer_len} ошибок)\n")
            out.write(f"   • CER (Character Error Rate): {cer:.2%} ({cer_dist}/{cer_len} ошибок)\n")
            
            # Детальный разбор ошибок
            if wer > 0:
                subs, dels, ins = align_words(ref.split(), hyp.split())
                all_subs.extend(subs)
                all_dels.extend(dels)
                all_ins.extend(ins)
                
                out.write(f"\n🔍 ДЕТАЛИ ОШИБОК:\n")
                if subs:
                    out.write(f"   🔄 ЗАМЕНЫ: {', '.join([f'{wrong}→{right}' for wrong, right in subs[:10]])}\n")
                if dels:
                    out.write(f"   ❌ ПРОПУСКИ: {', '.join(dels[:10])}\n")
                if ins:
                    out.write(f"   ➕ ВСТАВКИ: {', '.join(ins[:10])}\n")
            out.write("\n")
        
        # Итоговая статистика
        n = len(ref_lines)
        avg_wer = total_wer / n if n > 0 else 0
        avg_cer = total_cer / n if n > 0 else 0
        ser = sentences_with_errors / n if n > 0 else 0
        
        out.write("=" * 80 + "\n")
        out.write("📊 ИТОГОВАЯ СТАТИСТИКА\n")
        out.write("=" * 80 + "\n")
        out.write(f"📄 Всего предложений: {n}\n")
        out.write(f"🎯 Средний WER: {avg_wer:.2%}\n")
        out.write(f"✍️  Средний CER: {avg_cer:.2%}\n")
        out.write(f"⚠️  SER (предложения с ошибками): {ser:.2%}\n")
        
        # Оценка качества
        out.write("\n⭐ ОЦЕНКА КАЧЕСТВА:\n")
        if avg_wer <= 0.10:
            out.write("   🟢 Отлично! Ошибок очень мало, транскрибация высокого качества.\n")
        elif avg_wer <= 0.25:
            out.write("   🟡 Хорошо. Есть ошибки, но в целом качество приемлемое.\n")
        elif avg_wer <= 0.40:
            out.write("   🟠 Удовлетворительно. Много ошибок, требуется доработка.\n")
        else:
            out.write("   🔴 Плохо. Более 40% ошибок, транскрибация неудовлетворительная.\n")
        
        # Топ ошибок
        if all_subs:
            from collections import Counter
            out.write("\n🔝 ТОП-10 ЧАСТЫХ ОШИБОК:\n")
            sub_counter = Counter([f"{wrong}→{right}" for wrong, right in all_subs])
            for error, count in sub_counter.most_common(10):
                out.write(f"   • {error}: {count} раз(а)\n")
        
        out.write("\n" + "=" * 80 + "\n")
        out.write(f"✅ Отчет сохранен: {output_file}\n")
        out.write("=" * 80 + "\n")
    
    return output_file

def main():
    """Главная функция"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("=" * 60)
    print("🎙️  ASR QUALITY CHECKER - Оценка транскрибации")
    print("=" * 60)
    
    # Выбор файлов
    ref_file = get_file_from_user("Выберите ЭТАЛОННЫЙ файл (правильная транскрибация)")
    hyp_file = get_file_from_user("Выберите ПРОВЕРЯЕМЫЙ файл (результат работы ASR)")
    
    print(f"\n✅ Эталон: {ref_file}")
    print(f"✅ Проверяемый: {hyp_file}")
    
    # Спросить имя выходного файла
    custom_output = input("\nВведите имя выходного файла (Enter для автоматического): ").strip()
    
    print("\n🔄 Генерация отчета...")
    
    # Генерация отчета
    output_file = generate_report(ref_file, hyp_file, custom_output if custom_output else None)
    
    print(f"\n🎉 Готово! Отчет сохранен в: {output_file}")
    print(f"\n📂 Полный путь: {os.path.abspath(output_file)}")
    
    # Спросить, открыть ли файл
    open_file = input("\nОткрыть файл сейчас? (y/n): ").strip().lower()
    if open_file == 'y':
        if sys.platform == 'win32':
            os.startfile(output_file)
        elif sys.platform == 'darwin':
            os.system(f'open "{output_file}"')
        else:
            os.system(f'xdg-open "{output_file}"')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
