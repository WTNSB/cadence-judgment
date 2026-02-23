from models.note import parse_notes
from engine.analyzer import ChordAnalyzer

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