# engine/transition_analyzer.py
from typing import List
from models.note import Note
from engine.degree_converter import DegreeConverter
from dictionaries.cadence_dict import CADENCE_DICT # ★ 辞書をインポート

class TransitionAnalyzer:
    def __init__(self):
        self.MOVEMENT_NAMES = {
            0: "Common Tone (保留)",
            1: "m2 (半音)", 2: "M2 (全音)", 3: "m3 (短3度)", 4: "M3 (長3度)",
            5: "P4 (完全4度)", 6: "Tritone (トライトーン)", 7: "P5 (完全5度)",
            8: "m6 (短6度)", 9: "M6 (長6度)", 10: "m7 (短7度)", 11: "M7 (長7度)"
        }
        self.deg_conv = DegreeConverter()

    def _get_movement_str(self, diff: int) -> str:
        if diff == 0: return self.MOVEMENT_NAMES[0]
        direction = "Up" if diff > 0 else "Down"
        abs_diff = abs(diff)
        octave_shift = abs_diff // 12
        rem_diff = abs_diff % 12
        interval_name = self.MOVEMENT_NAMES.get(rem_diff, f"{rem_diff} semitones")
        octave_str = f" + {octave_shift}8va" if octave_shift > 0 else ""
        return f"{direction} {interval_name}{octave_str}"

    # --- ★ スコア優先順位付け ＋ 全候補の保持 ---
    def _evaluate_cadence(self, root_a: int, quality_a: str, root_b: int, quality_b: str, key_name: str) -> dict:
        key_root_pc = self.deg_conv._get_key_root_pc(key_name)
        
        roman_a = self.deg_conv.SEMITONE_TO_DEGREE[(root_a - key_root_pc) % 12]
        roman_b = self.deg_conv.SEMITONE_TO_DEGREE[(root_b - key_root_pc) % 12]
        
        best_match = None
        all_matches = [] # ★ マッチした全ての候補を保存するリスト

        # 1. 辞書からのマッチング探索
        for cadence in CADENCE_DICT:
            if cadence["from_degree"] != roman_a or cadence["to_degree"] != roman_b:
                continue
                
            from_q_match = any(q == quality_a or (q == "" and quality_a in ["", "Major"]) for q in cadence["from_quality"])
            if not from_q_match:
                continue
                
            if "to_quality_include" in cadence and cadence["to_quality_include"]:
                if not any(q in quality_b for q in cadence["to_quality_include"]):
                    continue
            if "to_quality_exclude" in cadence and cadence["to_quality_exclude"]:
                if any(q in quality_b for q in cadence["to_quality_exclude"]):
                    continue
                    
            # 条件に一致したものをリストに追加
            match_data = {"type": "Dict Match", "name": cadence["name"], "bonus": cadence["bonus"]}
            all_matches.append(match_data)
            
            if best_match is None or cadence["bonus"] > best_match["bonus"]:
                best_match = match_data

        if best_match:
            # ★ スコアが高い順にソートして、トップのデータに全候補リストをくっつけて返す
            all_matches.sort(key=lambda x: x['bonus'], reverse=True)
            best_match["all_matches"] = all_matches
            return best_match

        # 2. 辞書にない場合の汎用ルール
        root_diff = (root_b - root_a) % 12
        is_dominant_a = any(q in quality_a for q in ["7", "9", "11", "13", "aug7", "dim7"]) and "Maj" not in quality_a and "m7" not in quality_a

        fallback_match = None
        if root_diff == 5:
            if is_dominant_a:
                fallback_match = {"type": "Dominant Motion", "name": "強進行 (セブンスからの完全4度上)", "bonus": 15}
            else:
                fallback_match = {"type": "Strong Motion", "name": "強進行 (完全4度上)", "bonus": 10}
        elif root_diff == 2:
            fallback_match = {"type": "Stepwise Ascending", "name": "順次上行 (全音上)", "bonus": 5}
        elif root_diff == 10:
            fallback_match = {"type": "Stepwise Descending", "name": "順次下行 (全音下)", "bonus": 5}
        else:
            fallback_match = {"type": "Normal", "name": "一般的な進行", "bonus": 0}
            
        fallback_match["all_matches"] = [fallback_match] # フォーマットを合わせるため
        return fallback_match

    def analyze_transition(self, chord_a_root_pc: int, chord_a_quality: str, notes_a: List[Note], 
                                 chord_b_root_pc: int, chord_b_quality: str, notes_b: List[Note], 
                                 key_name: str = "C") -> str:
        
        # ... (前半のボイスリーディングのマッチング処理と score 計算部分はそのまま) ...
        # (※ここでは省略せずに、お手元のコードのまま残してください)
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

        # カデンツ評価の呼び出し
        cadence_info = self._evaluate_cadence(chord_a_root_pc, chord_a_quality, chord_b_root_pc, chord_b_quality, key_name)
        
        smoothness_score = 80 - (total_movement * 2) + (common_tones * 10)
        total_score = smoothness_score + cadence_info["bonus"]

        degree_a = self.deg_conv.convert_to_degree(chord_a_root_pc, chord_a_quality, key_name)
        degree_b = self.deg_conv.convert_to_degree(chord_b_root_pc, chord_b_quality, key_name)

        from utils.formatter import KeyContext
        kc = KeyContext(key_name)
        chord_a_name = f"{kc.get_note_name(chord_a_root_pc)}{chord_a_quality}"
        chord_b_name = f"{kc.get_note_name(chord_b_root_pc)}{chord_b_quality}"

        lines = [
            f"Context: Key of {key_name}",
            f"Transition: [ {chord_a_name} ]  ->  [ {chord_b_name} ]",
            f"Degree    : [ {degree_a} ]  ->  [ {degree_b} ]",
            f"Cadence   : {cadence_info['name']}"
        ]
        
        # --- ★ 追加: 他の候補（ダブり）があったら表示する ---
        if len(cadence_info.get("all_matches", [])) > 1:
            lines.append("  (Other Cadence Candidates:)")
            # 1番目（採用されたもの）以外をループで表示
            for match in cadence_info["all_matches"][1:]:
                lines.append(f"    - {match['name']} [Bonus: {match['bonus']}]")

        lines.extend([
            f"Score     : {total_score} (Voice Leading: {smoothness_score} + Cadence Bonus: {cadence_info['bonus']})",
            "-" * 40,
            "Voice Leading Details:"
        ])
        
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