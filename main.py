from models.note import parse_notes
from engine.analyzer import ChordAnalyzer
from engine.transition_analyzer import TransitionAnalyzer
# --- 実行テスト ---
if __name__ == "__main__":
    analyzer = ChordAnalyzer()
    

    messy_notes = parse_notes("D#4, Fx4, A#4")

    print("Key=C :", analyzer.analyze(messy_notes, key="C"))
    print("Key=Eb:", analyzer.analyze(messy_notes, key="Eb"))
    print("Test 17:", analyzer.analyze(parse_notes("C3, E3, Bb3, D4, F#4, A4"),key="C"))
    print("柴又テスト:", analyzer.analyze(parse_notes("G3, B3, D#4, F4, A#4"),key="G"))
    print("Test 14:", analyzer.analyze(parse_notes("C4, F4, Bb4, Eb5"),key="C"))
    print("Test 6:", analyzer.analyze(parse_notes("G4, B4, D5, F5, Ab5"),key="G")) # Dom7(b9)
    print("Test 9:", analyzer.analyze(parse_notes("G3, C4, E4"),key="G"))


    print("\n" + "="*50)
    print("--- カデンツ（和音遷移）詳細解析テスト ---")
    print("="*50)
    
    transition_analyzer = TransitionAnalyzer()
    
# main.py 

    # 柴又のサビ（Key = Eb Major）での進行テスト
    chord_a_notes = parse_notes("F3, C4, Eb4, Ab4")     # Fm7
    chord_b_notes = parse_notes("G3, B3, D#4, F4, A#4") # Gaug7(#9)
    
    # Fm7 は Fがルート(5)、Gaug7(#9) は Gがルート(7)
    report = transition_analyzer.analyze_transition(
        chord_a_root_pc=5, chord_a_quality="m7", notes_a=chord_a_notes,
        chord_b_root_pc=7, chord_b_quality="aug7(#9)", notes_b=chord_b_notes,
        key_name="Eb" # 柴又のKeyを指定
    )
    
    print(report)