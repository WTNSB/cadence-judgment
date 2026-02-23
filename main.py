from models.note import parse_notes
from engine.analyzer import ChordAnalyzer
from engine.transition_analyzer import TransitionAnalyzer
from engine.progression_analyzer import ProgressionAnalyzer
from engine.melody_analyzer import MelodyAnalyzer
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


    prog_analyzer = ProgressionAnalyzer()
    # 柴又の進行をそのままリストにするだけ！
    shibamata_prog = [
        "F3, C4, Eb4, Ab4",     # Fm7
        "G3, B3, D#4, F4, A#4", # Gaug7(#9)
        "C3, G3, Bb3, D4, Eb4", # Cm7(9)
        "Eb3, G3, Bb3, D4"      # EbM7
    ]
    
    # 自動判定・自動遷移解析
    print(prog_analyzer.analyze_progression(shibamata_prog, key="Eb"))
    print("\n" + "="*50)
    print("=== メロディ・アヴォイド判定テスト ===")
    print("="*50)

    melody_analyzer = MelodyAnalyzer()
    
    # C Major (C4, E4, G4) のデータを用意
    c_maj_notes = parse_notes("C4, E4, G4")
    
    print("【テストA】Cメジャーコード上で『D5』(9th) を弾いた場合")
    print(melody_analyzer.analyze_melody(
        melody_note=parse_notes("D5")[0],
        chord_root_pc=0,
        chord_quality="Major",
        chord_notes=c_maj_notes
    ))
    
    print("\n【テストB】Cメジャーコード上で『F5』(11th) を弾いた場合")
    print(melody_analyzer.analyze_melody(
        melody_note=parse_notes("F5")[0],
        chord_root_pc=0,
        chord_quality="Major",
        chord_notes=c_maj_notes
    ))