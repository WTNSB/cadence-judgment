# engine/degree_converter.py
from models.note import Note

class DegreeConverter:
    """
    絶対音程のコードをKey（調）に基づくディグリー（度数）ネームに変換するクラス
    """
    def __init__(self):
        # 主音からの半音差とローマ数字の対応表（ポピュラー音楽理論準拠）
        self.SEMITONE_TO_DEGREE = {
            0: "I",
            1: "bII",
            2: "II",
            3: "bIII",
            4: "III",
            5: "IV",
            6: "#IV", # トライトーン (bVとも表記される)
            7: "V",
            8: "bVI",
            9: "VI",
            10: "bVII",
            11: "VII"
        }
        
    def _get_key_root_pc(self, key_name: str) -> int:
        """Key名（例: 'Eb', 'F#m'）から主音のピッチクラスを取得"""
        # 'm' や 'Minor' が付いていても、主音のアルファベットだけを抽出する
        clean_key = key_name.replace("m", "").replace("Minor", "").replace(" ", "")
        # Noteクラスのパース機能を使ってピッチクラスを取得
        return Note.from_string(f"{clean_key}4").pitch_class

    def convert_to_degree(self, chord_root_pc: int, chord_quality: str, key_name: str, bass_pc: int = None) -> str:
        """
        コードのルートとクオリティからディグリーネームを生成する
        """
        key_root_pc = self._get_key_root_pc(key_name)
        
        # Keyの主音からコードのルートまでの半音差を計算
        diff = (chord_root_pc - key_root_pc) % 12
        degree_roman = self.SEMITONE_TO_DEGREE[diff]
        
        # クオリティを結合 (例: I + m7 = Im7)
        # Majorトライアドの場合はqualityが空文字（または "Major"）で入ってくることを想定
        clean_quality = chord_quality.replace("Major", "").strip() 
        degree_name = f"{degree_roman}{clean_quality}"
        
        # 分数コード（オンコードや転回形）の場合のベース音のディグリー表記
        if bass_pc is not None and bass_pc != chord_root_pc:
            bass_diff = (bass_pc - key_root_pc) % 12
            bass_degree_roman = self.SEMITONE_TO_DEGREE[bass_diff]
            degree_name += f" / {bass_degree_roman}"
            
        return degree_name