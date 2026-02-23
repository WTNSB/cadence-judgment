# engine/transition_analyzer.py
from typing import List
from models.note import Note
from engine.degree_converter import DegreeConverter

class TransitionAnalyzer:
    """
    2つの和音間の遷移（ボイスリーディングとルートモーション）を解析するクラス
    """
    def __init__(self):
        # 半音の差分（絶対値）をインターバル名に変換する辞書
        self.MOVEMENT_NAMES = {
            0: "Common Tone (保留)",
            1: "m2 (半音)", 2: "M2 (全音)", 3: "m3 (短3度)", 4: "M3 (長3度)",
            5: "P4 (完全4度)", 6: "Tritone (トライトーン)", 7: "P5 (完全5度)",
            8: "m6 (短6度)", 9: "M6 (長6度)", 10: "m7 (短7度)", 11: "M7 (長7度)"
        }

    def _get_movement_str(self, diff: int) -> str:
        if diff == 0:
            return self.MOVEMENT_NAMES[0]
        
        direction = "Up" if diff > 0 else "Down"
        abs_diff = abs(diff)
        
        octave_shift = abs_diff // 12
        rem_diff = abs_diff % 12
        
        interval_name = self.MOVEMENT_NAMES.get(rem_diff, f"{rem_diff} semitones")
        octave_str = f" + {octave_shift}8va" if octave_shift > 0 else ""
        
        return f"{direction} {interval_name}{octave_str}"

    # 引数に key_name とコードのルート/クオリティ情報を追加
    def analyze_transition(self, chord_a_root_pc: int, chord_a_quality: str, notes_a: List[Note], 
                                 chord_b_root_pc: int, chord_b_quality: str, notes_b: List[Note], 
                                 key_name: str = "C") -> str:
        
        unmatched_a = list(notes_a)
        unmatched_b = list(notes_b)
        mappings = []
        
        # 1. 共通音（ピッチが完全に一致するもの、異名同音含む）を優先してマッチング
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

        # 2. 残った音に対して、最も移動距離（半音差）が少ない音を貪欲にマッチング
        for nb in list(unmatched_b):
            if not unmatched_a:
                mappings.append((None, nb, None)) # Chord Aに音が足りない場合
                continue
            
            # Chord Bの音に対して、最も近いChord Aの音を探す
            unmatched_a.sort(key=lambda na: abs(na.absolute_semitone - nb.absolute_semitone))
            best_match = unmatched_a.pop(0)
            diff = nb.absolute_semitone - best_match.absolute_semitone
            mappings.append((best_match, nb, diff))

        # 3. Chord Aに余った音がある場合（音が消滅した場合）
        for na in unmatched_a:
            mappings.append((na, None, None))

        # --- スコアリング計算 ---
        # 共通音が多いほど加点、全体の移動距離（半音数）が少ないほど滑らかとして加点
        total_movement = 0
        common_tones = 0
        
        for ma, mb, diff in mappings:
            if diff == 0:
                common_tones += 1
            elif diff is not None:
                total_movement += abs(diff)
                
        # 基礎スコア80点から、滑らかさを計算
        smoothness_score = 80 - (total_movement * 2) + (common_tones * 10)

        # --- ディグリー変換の実行 ---
        deg_conv = DegreeConverter()
        degree_a = deg_conv.convert_to_degree(chord_a_root_pc, chord_a_quality, key_name)
        degree_b = deg_conv.convert_to_degree(chord_b_root_pc, chord_b_quality, key_name)

        # 便宜上の絶対コードネームも作っておく
        from utils.formatter import KeyContext
        kc = KeyContext(key_name)
        chord_a_name = f"{kc.get_note_name(chord_a_root_pc)}{chord_a_quality}"
        chord_b_name = f"{kc.get_note_name(chord_b_root_pc)}{chord_b_quality}"

        # --- 出力フォーマットの作成 ---
        lines = [
            f"Context: Key of {key_name}",
            f"Transition: [ {chord_a_name} ]  ->  [ {chord_b_name} ]",
            f"Degree    : [ {degree_a} ]  ->  [ {degree_b} ]",  # ★ ディグリーの動きを追加！
            f"Smoothness Score: {smoothness_score}",
            "-" * 40,
            "Voice Leading Details:"
        ]
        
        # 見やすいように、音が高い順（上から下）にソートして表示
        mappings.sort(key=lambda m: m[1].absolute_semitone if m[1] else m[0].absolute_semitone, reverse=True)
        
        for ma, mb, diff in mappings:
            if ma and mb:
                mov_str = self._get_movement_str(diff)
                # 異名同音の表記ゆれチェック（Eb -> D# のような動きは保留扱い）
                if diff == 0 and ma.step != mb.step:
                    mov_str += " (Enharmonic Equivalents)"
                lines.append(f"  {str(ma):<5} ->  {str(mb):<5} : {mov_str}")
            elif mb:
                lines.append(f"  (New) ->  {str(mb):<5} : Appears")
            elif ma:
                lines.append(f"  {str(ma):<5} ->  (End) : Disappears")

        return "\n".join(lines)