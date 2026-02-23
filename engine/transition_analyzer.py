# engine/transition_analyzer.py
from typing import List
from models.note import Note
from engine.degree_converter import DegreeConverter

class TransitionAnalyzer:
    def __init__(self):
        self.MOVEMENT_NAMES = {
            0: "Common Tone (保留)",
            1: "m2 (半音)", 2: "M2 (全音)", 3: "m3 (短3度)", 4: "M3 (長3度)",
            5: "P4 (完全4度)", 6: "Tritone (トライトーン)", 7: "P5 (完全5度)",
            8: "m6 (短6度)", 9: "M6 (長6度)", 10: "m7 (短7度)", 11: "M7 (長7度)"
        }

    def _get_movement_str(self, diff: int) -> str:
        if diff == 0: return self.MOVEMENT_NAMES[0]
        direction = "Up" if diff > 0 else "Down"
        abs_diff = abs(diff)
        octave_shift = abs_diff // 12
        rem_diff = abs_diff % 12
        interval_name = self.MOVEMENT_NAMES.get(rem_diff, f"{rem_diff} semitones")
        octave_str = f" + {octave_shift}8va" if octave_shift > 0 else ""
        return f"{direction} {interval_name}{octave_str}"

    # --- ★ 新規追加: カデンツ（進行）の評価ロジック ---
    def _evaluate_cadence(self, root_a: int, quality_a: str, root_b: int) -> dict:
        root_diff = (root_b - root_a) % 12
        
        # Chord A がドミナント機能（3度と短7度を持つセブンス）を持っているか判定
        is_dominant_a = any(q in quality_a for q in ["7", "9", "11", "13", "aug7", "dim7"]) and "Maj" not in quality_a and "m7" not in quality_a

        # 1. 強進行 (完全4度上 / 完全5度下) = 5半音
        if root_diff == 5:
            if is_dominant_a:
                return {"type": "Dominant Motion", "name": "ドミナント・モーション (強進行・解決)", "bonus": 30}
            else:
                return {"type": "Strong Motion", "name": "強進行 (完全4度上)", "bonus": 15}
        
        # 2. 裏コード解決 (半音下) = 11半音
        elif root_diff == 11 and is_dominant_a:
             return {"type": "Tritone Substitution", "name": "裏コードからの解決 (半音下)", "bonus": 25}
             
        # 3. 順次進行 (全音上 / 全音下) = 2半音 / 10半音
        elif root_diff == 2:
             return {"type": "Stepwise Ascending", "name": "順次上行 (全音上)", "bonus": 10}
        elif root_diff == 10:
             return {"type": "Stepwise Descending", "name": "順次下行 (全音下)", "bonus": 10}
             
        # 4. 偽終止などの特殊な動き（短3度上など）
        elif root_diff == 3:
             return {"type": "Minor 3rd Up", "name": "短3度上行 (代理コードへの進行など)", "bonus": 5}

        return {"type": "Normal", "name": "一般的な進行", "bonus": 0}

    def analyze_transition(self, chord_a_root_pc: int, chord_a_quality: str, notes_a: List[Note], 
                                 chord_b_root_pc: int, chord_b_quality: str, notes_b: List[Note], 
                                 key_name: str = "C") -> str:
        
        unmatched_a = list(notes_a)
        unmatched_b = list(notes_b)
        mappings = []

        for nb in list(unmatched_b):
            best_match = None
            for na in unmatched_a:
                if na.absolute_semitone == nb.absolute_semitone:
                    best_match = na
                    break
            if best_match:
                mappings.append((best_match, nb, 0))
                unmatched_a.remove(best_match)
                unmatched_b.remove(nb)

        for nb in list(unmatched_b):
            if not unmatched_a:
                mappings.append((None, nb, None))
                continue
            unmatched_a.sort(key=lambda na: abs(na.absolute_semitone - nb.absolute_semitone))
            best_match = unmatched_a.pop(0)
            diff = nb.absolute_semitone - best_match.absolute_semitone
            mappings.append((best_match, nb, diff))

        for na in unmatched_a:
            mappings.append((na, None, None))

        total_movement = 0
        common_tones = 0
        for ma, mb, diff in mappings:
            if diff == 0:
                common_tones += 1
            elif diff is not None:
                total_movement += abs(diff)
                
        # --- ★ 変更: カデンツ評価の組み込み ---
        cadence_info = self._evaluate_cadence(chord_a_root_pc, chord_a_quality, chord_b_root_pc)
        
        # ボイスリーディングの滑らかさスコア + カデンツ（機能和声）としての強さボーナス
        smoothness_score = 80 - (total_movement * 2) + (common_tones * 10)
        total_score = smoothness_score + cadence_info["bonus"]

        deg_conv = DegreeConverter()
        degree_a = deg_conv.convert_to_degree(chord_a_root_pc, chord_a_quality, key_name)
        degree_b = deg_conv.convert_to_degree(chord_b_root_pc, chord_b_quality, key_name)

        from utils.formatter import KeyContext
        kc = KeyContext(key_name)
        chord_a_name = f"{kc.get_note_name(chord_a_root_pc)}{chord_a_quality}"
        chord_b_name = f"{kc.get_note_name(chord_b_root_pc)}{chord_b_quality}"

        lines = [
            f"Context: Key of {key_name}",
            f"Transition: [ {chord_a_name} ]  ->  [ {chord_b_name} ]",
            f"Degree    : [ {degree_a} ]  ->  [ {degree_b} ]",
            f"Cadence   : {cadence_info['name']}", # ★ 追加: カデンツの種類を表示
            f"Score     : {total_score} (Voice Leading: {smoothness_score} + Cadence Bonus: {cadence_info['bonus']})",
            "-" * 40,
            "Voice Leading Details:"
        ]
        
        mappings.sort(key=lambda m: m[1].absolute_semitone if m[1] else m[0].absolute_semitone, reverse=True)
        
        for ma, mb, diff in mappings:
            if ma and mb:
                mov_str = self._get_movement_str(diff)
                if diff == 0 and ma.step != mb.step:
                    mov_str += " (Enharmonic Equivalents)"
                lines.append(f"  {str(ma):<5} ->  {str(mb):<5} : {mov_str}")
            elif mb:
                lines.append(f"  (New) ->  {str(mb):<5} : Appears")
            elif ma:
                lines.append(f"  {str(ma):<5} ->  (End) : Disappears")

        return "\n".join(lines)