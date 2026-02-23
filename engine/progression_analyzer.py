from engine.analyzer import ChordAnalyzer
from engine.transition_analyzer import TransitionAnalyzer
from models.note import parse_notes # これは一つ上の階層なので、実行方法によっては修正が必要（後述）

class ProgressionAnalyzer:
    """
    複数のコード進行（文字列のリスト）を受け取り、
    自動的にコード判定と遷移解析を連鎖させるクラス
    """
    def __init__(self):
        self.chord_analyzer = ChordAnalyzer()
        self.transition_analyzer = TransitionAnalyzer()

    def analyze_progression(self, progression_list: list, key: str = "C"):
        reports = []
        previous_chord_data = None

        for i, notes_str in enumerate(progression_list):
            notes = parse_notes(notes_str)
            
            # 1. コードを自動判定（最もスコアの高いものを採用）
            current_chord_data = self.chord_analyzer.get_best_interpretation(notes, key=key)
            
            if not current_chord_data:
                reports.append(f"Chord {i+1}: Unknown chord [{notes_str}]")
                previous_chord_data = None
                continue

            # 2. 判定結果を表示
            reports.append(f"--- Chord {i+1}: {current_chord_data['name']} (Score: {current_chord_data['score']}) ---")

            # 3. 前のコードがあれば、遷移解析を自動実行
            if previous_chord_data:
                transition_report = self.transition_analyzer.analyze_transition(
                    chord_a_root_pc=previous_chord_data['root_pc'],
                    chord_a_quality=previous_chord_data['quality'],
                    notes_a=previous_chord_data['notes'],
                    chord_b_root_pc=current_chord_data['root_pc'],
                    chord_b_quality=current_chord_data['quality'],
                    notes_b=current_chord_data['notes'],
                    key_name=key
                )
                reports.append(transition_report)
                reports.append("\n")

            previous_chord_data = current_chord_data

        return "\n".join(reports)