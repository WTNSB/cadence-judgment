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
        self.chord_dictionary = CHORD_DICT # 先ほど定義した辞書

        # (ステップ差, 半音差) を度数名に変換する2次元マッピング
        # P: Perfect, M: Major, m: minor, d: diminished, A: Augmented
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
        """ 2つの音符間の厳密な度数を計算する """
        # 五線譜上のステップ差 (0=1度, 1=2度, ... 6=7度)
        step_diff = (target.step_index - root.step_index) % 7
        
        # 鍵盤上の半音差
        semi_diff = (target.absolute_semitone - root.absolute_semitone) % 12
        
        return self.INTERVAL_MAP.get((step_diff, semi_diff), f"Unknown({step_diff},{semi_diff})")

    def analyze(self, notes: List[Note]) -> str:
        if not notes: return "No notes"

        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        root_note = sorted_notes[0] # まだ一番下の音をルートと仮定

        intervals = set()
        for note in sorted_notes:
            intervals.add(self._get_interval(root_note, note))

        quality = self.chord_dictionary.get(frozenset(intervals), "Unknown")
        
        alter_str = "#" if root_note.alter == 1 else "b" if root_note.alter == -1 else ""
        root_name = f"{root_note.step}{alter_str}"
        notes_str = ", ".join(str(n) for n in sorted_notes)
        intervals_str = ", ".join(intervals)

        return f"Input: [{notes_str}] -> Intervals: [{intervals_str}] -> Analyzed: {root_name} {quality}"

# --- 3. 異名同音のテスト ---
if __name__ == "__main__":
    analyzer = ChordAnalyzer()

    # テスト1: 普通のCメジャー
    print("Test 1:", analyzer.analyze(parse_notes("C, E, G")))
    
    # テスト2: EをFbに変えた場合（半音数は同じだが、度数が異なる）
    print("Test 2:", analyzer.analyze(parse_notes("C, Fb, G")))

    # テスト3: ディミニッシュコード（厳密な度数が機能しているか）
    print("Test 3:", analyzer.analyze(parse_notes("B, D, F, Ab")))