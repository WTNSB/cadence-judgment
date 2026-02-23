from engine.analyzer import ChordAnalyzer
from engine.progression_analyzer import ProgressionAnalyzer
from models.note import parse_notes

def main():
    analyzer = ChordAnalyzer()

    print("=== 単体コード解析のテスト ===")
    
    # analyze() は (解析文, 生データ) のタプルを返すので、
    # 表示したいのは最初の [0] (解析文) だけです。
    messy_notes = parse_notes("D#4, Fx4, A#4")
    print("Key=C :", analyzer.analyze(messy_notes, key="C")[0])
    print("Key=Eb:", analyzer.analyze(messy_notes, key="Eb")[0])
    
    print("Test 17 (UST):", analyzer.analyze(parse_notes("C3, E3, Bb3, D4, F#4, A4"), key="C")[0])
    print("柴又（単体）:", analyzer.analyze(parse_notes("G3, B3, D#4, F4, A#4"), key="G")[0])
    
    print("\n" + "="*50)
    print("=== 進行自動解析（柴又テスト） ===")
    print("="*50)

    prog_analyzer = ProgressionAnalyzer()
    
    # 音の並びをリスト化
    shibamata_prog = [
        "F3, C4, Eb4, Ab4",     # Fm7
        "G3, B3, D#4, F4, A#4", # Gaug7(#9)
        "C3, G3, Bb3, D4, Eb4", # Cm7(9)
        "Eb3, G3, Bb3, D4"      # EbM7
    ]
    
    # ProgressionAnalyzer 内で get_best_interpretation が動き、
    # 自動で全コードを判定して、間の遷移（ボイスリーディング・カデンツ）を解析します。
    report = prog_analyzer.analyze_progression(shibamata_prog, key="Eb")
    print(report)

if __name__ == "__main__":
    main()