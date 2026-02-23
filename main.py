import re
# main.py の一番上に追加
from dictionaries.chord_dict import CHORD_DICT
from dataclasses import dataclass
from typing import List, Optional

# --- 1. データ構造 ---
@dataclass
class Note:
    step: str
    alter: int
    octave: int

    def __post_init__(self):
        self.step = self.step.upper()

    STEP_TO_SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    STEP_TO_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

    @property
    def pitch_class(self) -> int:
        return (self.STEP_TO_SEMITONE[self.step] + self.alter) % 12

    @property
    def absolute_semitone(self) -> int:
        base = self.STEP_TO_SEMITONE[self.step]
        return base + self.alter + (self.octave * 12)

    @property
    def step_index(self) -> int:
        """ Cを0としたときの、五線譜上の基本音名のインデックス """
        return self.STEP_TO_INDEX[self.step]

    def __str__(self):
        alter_str = ""
        if self.alter == 1: alter_str = "#"
        elif self.alter == -1: alter_str = "b"
        elif self.alter == 2: alter_str = "x"
        elif self.alter == -2: alter_str = "bb"
        return f"{self.step}{alter_str}{self.octave}"

    @classmethod
    def from_string(cls, note_str: str, default_octave: Optional[int] = None) -> 'Note':
        match = re.match(r"^([a-gA-G])([#bx]*)(-?\d+)?$", note_str.strip())
        if not match: raise ValueError(f"Invalid format: '{note_str}'")
        step_str, alter_str, octave_str = match.groups()
        alter = {'': 0, '#': 1, 'b': -1, 'bb': -2, 'x': 2}.get(alter_str.lower(), 0)
        octave = int(octave_str) if octave_str is not None else default_octave
        if octave is None: octave = 4 
        return cls(step=step_str, alter=alter, octave=octave)

def parse_notes(notes_csv: str, start_octave: int = 4) -> List[Note]:
    note_strs = [s.strip() for s in notes_csv.split(",")]
    notes = []
    current_octave = start_octave
    last_pc = -1
    for n_str in note_strs:
        temp_note = Note.from_string(n_str, default_octave=None)
        if re.search(r"-?\d+$", n_str) is None:
            if temp_note.pitch_class < last_pc:
                current_octave += 1
            temp_note.octave = current_octave
            last_pc = temp_note.pitch_class
        else:
            current_octave = temp_note.octave
            last_pc = temp_note.pitch_class
        notes.append(temp_note)
    return notes

# --- 2. 推論エンジン（ここが大きく進化！） ---
class ChordAnalyzer:
    def __init__(self):
        self.chord_dictionary = CHORD_DICT

        self.INTERVAL_MAP = {
            (0, 0): 'P1',  (0, 1): 'A1',  (0, -1): 'd1',
            (1, 1): 'm2',  (1, 2): 'M2',  (1, 3): 'A2',  (1, 0): 'd2',
            (2, 3): 'm3',  (2, 4): 'M3',  (2, 5): 'A3',  (2, 2): 'd3',
            (3, 5): 'P4',  (3, 6): 'A4',  (3, 4): 'd4',
            (4, 7): 'P5',  (4, 8): 'A5',  (4, 6): 'd5',
            (5, 8): 'm6',  (5, 9): 'M6',  (5, 10): 'A6', (5, 7): 'd6',
            (6, 10): 'm7', (6, 11): 'M7', (6, 12): 'A7', (6, 9): 'd7'
        }

    def _get_interval(self, root: Note, target: Note) -> str:
        # 1. 1オクターブ内に丸めた基本度数を計算
        step_diff = (target.step_index - root.step_index) % 7
        semi_diff = (target.absolute_semitone - root.absolute_semitone) % 12
        
        base_interval = self.INTERVAL_MAP.get((step_diff, semi_diff))
        if not base_interval:
            return f"Unknown({step_diff},{semi_diff})"
            
        # 2. 実際の半音差から、オクターブを超えているか判定
        actual_semi_diff = target.absolute_semitone - root.absolute_semitone
        
        quality = base_interval[0] # 'P', 'M', 'm', 'A', 'd'
        number = int(base_interval[1:]) # 1, 2, 3, 4, 5, 6, 7
        
        # 3. テンションの正規化
        # ルートより1オクターブ以上高く、かつ 2, 4, 6度の場合は 9, 11, 13度に変換
        if actual_semi_diff >= 12 and number in [2, 4, 6]:
            return f"{quality}{number + 7}"
            
        # 1, 3, 5, 7度は何オクターブ離れていても基本度数のまま返す
        return base_interval

    def analyze(self, notes: List[Note], threshold: int = 40) -> str:
        if not notes: return "No notes"

        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        bass_note = sorted_notes[0]
        bass_alter_str = "#" if bass_note.alter == 1 else "b" if bass_note.alter == -1 else ""
        bass_name = f"{bass_note.step}{bass_alter_str}"
        
        spread = sorted_notes[-1].absolute_semitone - sorted_notes[0].absolute_semitone
        voicing_type = "Open" if spread > 12 else "Closed"

        input_pcs = {n.pitch_class for n in sorted_notes}
        unique_cands = {n.pitch_class: n for n in sorted_notes}

        # 結果を格納するカテゴリー別の辞書
        categorized_results = {
            "基本形 (Root Position)": [],
            "転回形 (Inversion)": [],
            "オンコード (On-Chord)": [],
            "ルートレス (Rootless)": [],
            "特殊形 (Special)": []
        }

        # --- ヘルパー関数: カテゴリーの判定 ---
        def get_category(is_root_position, is_rootless, quality, intervals, dummy_root_pc):
            # 1. 特殊形 (Quartal, クラシック増6和音など)
            if any(sq in quality for sq in ["Quartal", "Quintal", "+6", "Cluster"]):
                return "特殊形 (Special)"
            
            # 2. ルートレス
            if is_rootless:
                return "ルートレス (Rootless)"
                
            # 3. 基本形
            if is_root_position:
                return "基本形 (Root Position)"
                
            # 4. 転回形 vs オンコード の判定
            # ベース音がコードトーン(M3, m3, P5, d5, A5, m7, M7)なら「転回形」、それ以外(テンションなど)なら「オンコード」とみなす
            bass_interval = (bass_note.pitch_class - dummy_root_pc) % 12
            chord_tone_intervals = {3, 4, 6, 7, 8, 10, 11} # 半音数でのコードトーン
            if bass_interval in chord_tone_intervals:
                return "転回形 (Inversion)"
            else:
                return "オンコード (On-Chord)"

        # ==========================================
        # 1. 通常探索 (基本形 / 転回形 / オンコード / 特殊形)
        # ==========================================
        for root_pc, cand in unique_cands.items():
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = set()
            for note in sorted_notes:
                intervals.add(self._get_interval(dummy_root, note))
                
            cand_alter_str = "#" if cand.alter == 1 else "b" if cand.alter == -1 else ""
            root_name = f"{cand.step}{cand_alter_str}"
            is_root_pos = (root_pc == bass_note.pitch_class)
            
            # A. 完全一致
            quality = self.chord_dictionary.get(frozenset(intervals))
            if quality:
                category = get_category(is_root_pos, False, quality, intervals, root_pc)
                score = 80 if is_root_pos else 60
                
                # 特殊形はベースが何であれオンコード表記にしない(例外処理)
                if category == "特殊形 (Special)":
                    name = f"{quality} on {bass_name}"
                    score = 75 # 意図的なボイシングとして高く評価
                else:
                    name = f"{root_name} {quality}" if is_root_pos else f"{root_name} {quality} / {bass_name}"
                    
                categorized_results[category].append({"name": f"{name} ({voicing_type})", "score": score})
            
            # B. Omit5 補完
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality_omit = self.chord_dictionary.get(frozenset(intervals_with_p5))
                
                if quality_omit:
                    category = get_category(is_root_pos, False, quality_omit, intervals_with_p5, root_pc)
                    score = 65 if is_root_pos else 45 # Omitペナルティ
                    name = f"{root_name} {quality_omit}(omit5)" if is_root_pos else f"{root_name} {quality_omit}(omit5) / {bass_name}"
                    categorized_results[category].append({"name": f"{name} ({voicing_type})", "score": score})

        # ==========================================
        # 2. ルートレス探索
        # ==========================================
        missing_pcs = [pc for pc in range(12) if pc not in input_pcs]
        phantom_map = {0:('C',0), 1:('C',1), 2:('D',0), 3:('E',-1), 4:('E',0), 5:('F',0), 6:('F',1), 7:('G',0), 8:('A',-1), 9:('A',0), 10:('B',-1), 11:('B',0)}
        
        for phantom_pc in missing_pcs:
            p_step, p_alter = phantom_map[phantom_pc]
            phantom_root = Note(p_step, p_alter, bass_note.octave)
            if phantom_root.absolute_semitone > bass_note.absolute_semitone:
                phantom_root.octave -= 1
                
            intervals = {'P1'}
            for note in sorted_notes:
                intervals.add(self._get_interval(phantom_root, note))
                
            quality = self.chord_dictionary.get(frozenset(intervals))
            is_omit5 = False
            
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality = self.chord_dictionary.get(frozenset(intervals_with_p5))
                if quality: is_omit5 = True

            if quality and any(ext in quality for ext in ['7', '9', '11', '13', 'dim']):
                p_alter_str = "#" if p_alter == 1 else "b" if p_alter == -1 else ""
                root_name = f"{p_step}{p_alter_str}"
                
                # テンションボーナス
                tension_bonus = 0
                if '9' in quality: tension_bonus += 10
                if '11' in quality: tension_bonus += 15
                if '13' in quality: tension_bonus += 20
                
                # ルートレスの基礎点(30) + テンションボーナス - Omit5ペナルティ(-10)
                score = 30 + tension_bonus - (10 if is_omit5 else 0)
                
                omit_str = "(omit5)" if is_omit5 else ""
                name = f"{root_name} {quality}{omit_str}(Rootless) / {bass_name}"
                categorized_results["ルートレス (Rootless)"].append({"name": f"{name} ({voicing_type})", "score": score})

        # ==========================================
        # 3. 出力のフォーマット (閾値フィルタリング)
        # ==========================================
        notes_str = ", ".join(str(n) for n in sorted_notes)
        output_lines = [f"Input: [{notes_str}] (Bass: {bass_name})"]
        output_lines.append(f"{'-'*40}")
        
        has_results = False
        for category, results in categorized_results.items():
            # 閾値でフィルタリングし、スコア降順にソート
            filtered_results = sorted([r for r in results if r['score'] >= threshold], key=lambda x: x['score'], reverse=True)
            
            if filtered_results:
                has_results = True
                output_lines.append(f"■ {category}")
                # 重複排除しながら出力
                seen = set()
                for res in filtered_results:
                    if res['name'] not in seen:
                        seen.add(res['name'])
                        output_lines.append(f"  - {res['name']} [Score: {res['score']}]")

        if not has_results:
            output_lines.append(f"Analyzed: Unknown (No interpretation scored above {threshold})")
            
        output_lines.append(f"{'-'*40}")
        return "\n".join(output_lines)
        # ==========================================
        # 結果のフォーマットと出力
        # ==========================================
        notes_str = ", ".join(str(n) for n in sorted_notes)

        if not found_chords:
            return f"Input: [{notes_str}] -> Analyzed: Unknown (Bass: {bass_name}) [Score: 0]"
        
        # スコアが高い順にソート(同点の場合は名前順)
        found_chords.sort(key=lambda x: (x["score"], x["name"]), reverse=True)
        
        # 重複解釈の排除
        unique_results = []
        seen = set()
        for c in found_chords:
            if c["name"] not in seen:
                seen.add(c["name"])
                unique_results.append(c)
        
        best_chord = f"{unique_results[0]['name']} [Score: {unique_results[0]['score']}]"
        
        if len(unique_results) > 1:
            # 代替候補も上位3つまでスコア付きで表示
            alternatives = ", ".join(f"{c['name']} [Score: {c['score']}]" for c in unique_results[1:4])
            return f"Input: [{notes_str}] -> Analyzed: {best_chord} (Alternatives: {alternatives})"
        else:
            return f"Input: [{notes_str}] -> Analyzed: {best_chord}"
# --- 実行テスト ---
if __name__ == "__main__":
    analyzer = ChordAnalyzer()
    
    # 以前のテスト
    print("Test 1:", analyzer.analyze(parse_notes("C, E, G")))
    print("Test 2:", analyzer.analyze(parse_notes("C, Fb, G")))
    print("Test 3:", analyzer.analyze(parse_notes("B4, D5, F5, Ab5")))

    # 今回のテンションテスト
    print("Test 4:", analyzer.analyze(parse_notes("C4, E4, G4, D5"))) # Add9
    print("Test 5:", analyzer.analyze(parse_notes("C4, E4, G4, B4, D5"))) # Maj9
    print("Test 6:", analyzer.analyze(parse_notes("G4, B4, D5, F5, Ab5"))) # Dom7(b9)
    print("Test 7:", analyzer.analyze(parse_notes("C4, G4, E5"))) # C Major (E5がM3に正規化されるか)
    # テスト8: Cメジャーの第一転回形 (ミ・ソ・ド)
    print("Test 8:", analyzer.analyze(parse_notes("E4, G4, C5")))
    
    # テスト9: Cメジャーの第二転回形 (ソ・ド・ミ)
    print("Test 9:", analyzer.analyze(parse_notes("G3, C4, E4")))
    
    # テスト10: テンションを含む複雑なオンコード (C Dom9 / E)
    print("Test 10:", analyzer.analyze(parse_notes("E3, Bb3, C4, D4, G4")))

    # テスト11: 入力順がバラバラでも自動でソートしてベース音を判定できるか
    print("Test 11:", analyzer.analyze(parse_notes("C4, G3, E4")))
    # テスト12: エッジケース1 (C, E, G, A)
    # ルートポジションである C6 が第一候補、Am7 / C が代替候補になるか検証
    print("Test 12:", analyzer.analyze(parse_notes("C4, E4, G4, A4")))

    # テスト13: エッジケース2 (B, D, F, G)
    # G Dom7 / B と B m7b5 (今回はm6がないのでどう解釈されるか) などの複数解釈の検証
    # ※辞書に G Dom7 があれば G Dom7 / B と解釈され、もし G7等がない場合は Unknown 等になります
    print("Test 13:", analyzer.analyze(parse_notes("B3, D4, F4, G4")))
    print("--- 4度堆積と特殊系のテスト ---")
    
    # テスト14: 4度堆積 (C4, F4, Bb4, Eb5)
    # 3度堆積で無理やり解釈すれば Cm11(omit5) にもなりますが、Quartal としてスマートに解釈します。
    print("Test 14:", analyzer.analyze(parse_notes("C4, F4, Bb4, Eb5")))

    # テスト15: 5度堆積 (C4, G4, D5)
    # Sus2やAdd9(omit3)とも解釈できますが、5度堆積として独立させました。
    print("Test 15:", analyzer.analyze(parse_notes("C4, G4, D5")))

    # テスト16: ドイツの増6の和音 vs ドミナントセブンス
    # 鍵盤で弾くと同じ音（Ab, C, Eb, Gb/F#）ですが、記譜（意味）が異なります！
    
    # 1. Ab ドミナントセブンス (Ab, C, Eb, Gb) -> m7 が含まれる
    print("Test 16-1:", analyzer.analyze(parse_notes("Ab3, C4, Eb4, Gb4")))
    
    # 2. Ab ベースのドイツの増6 (Ab, C, Eb, F#) -> A6 (増6度) が含まれる
    print("Test 16-2:", analyzer.analyze(parse_notes("Ab3, C4, Eb4, F#4")))
