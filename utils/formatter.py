# utils/formatter.py

class KeyContext:
    """
    指定されたKey（調性）に基づいて、ピッチクラスを適切な音名文字列にフォーマットするクラス
    """
    def __init__(self, key_name: str = "C"):
        self.key_name = key_name
        self.use_flats = self._determine_flat_key(key_name)

    def _determine_flat_key(self, key_name: str) -> bool:
        # フラット記号を優先して使う調性のリスト
        flat_keys = ["F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb", 
                     "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm"]
        return key_name in flat_keys

    def get_note_name(self, pitch_class: int) -> str:
        pitch_class = pitch_class % 12
        
        if self.use_flats:
            # フラット系の基本スペリング
            spellings = {0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F', 
                         6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}
            
            # 特殊ケース: Gbメジャーなどの調では、BではなくCbを使う
            if self.key_name in ["Gb", "Ebm", "Cb", "Abm"]:
                spellings[11] = 'Cb'
                
            return spellings[pitch_class]
        else:
            # シャープ系の基本スペリング
            spellings = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 
                         6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
                         
            # 特殊ケース: F#メジャーなどの調では、FではなくE#を使う（必要に応じて拡張可能）
            if self.key_name in ["F#", "D#m"]:
                spellings[5] = 'E#'
                
            return spellings[pitch_class]