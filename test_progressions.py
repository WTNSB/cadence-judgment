from engine.progression_analyzer import ProgressionAnalyzer
from models.note import parse_notes

def main():
    prog_analyzer = ProgressionAnalyzer()

    # 1. 4536進行 (Secondary Dominantの解釈確認)
    print("="*60)
    print("【4536進行】: III7へのセカンダリードミナント解釈の確認")
    print("="*60)
    prog_4536 = [
        "F3, A3, C4, E4",   # IV Maj7
        "G3, B3, D4, F4",   # V 7
        "E3, G#3, B3, D4",  # III 7 (Secondary Dominant)
        "A3, C4, E4, G4"    # VI m7
    ]
    print(prog_analyzer.analyze_progression(prog_4536, key="C"))

    # 2. 4563進行 (偽終止と弱進行の解釈確認)
    print("\n" + "="*60)
    print("【4563進行】: 偽終止からトニック代理(IIIm)への着地")
    print("="*60)
    prog_4563 = [
        "F3, A3, C4, E4",   # IV Maj7
        "G3, B3, D4, F4",   # V 7
        "A3, C4, E4, G4",   # VI m7
        "E3, G3, B3, D4"    # III m7 (弱進行)
    ]
    print(prog_analyzer.analyze_progression(prog_4563, key="C"))

    # 3. エオリアン・カデンツ (同主短調借用の連鎖)
    print("\n" + "="*60)
    print("【借用進行】: bVI -> bVII -> I (エオリアン・カデンツ)")
    print("="*60)
    prog_modal = [
        "Ab3, C4, Eb4, G4", # bVI Maj7
        "Bb3, D4, F4, Ab4", # bVII 7
        "C3, E4, G4, B4"    # I Maj7
    ]
    print(prog_analyzer.analyze_progression(prog_modal, key="C"))

    # 4. 「えぐい」接続の確認 (bVII -> V)
    print("\n" + "="*60)
    print("【特殊接続】: bVII -> V (ドミナントへのえぐい回帰)")
    print("="*60)
    prog_egui = [
        "Bb3, D4, F4, A4",  # bVII Maj7
        "G3, B3, D4, F4"    # V 7
    ]
    print(prog_analyzer.analyze_progression(prog_egui, key="C"))

if __name__ == "__main__":
    main()