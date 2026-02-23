# engine/melody_analyzer.py
from typing import List
from models.note import Note
from utils.interval_calc import get_interval
from dictionaries.interval_dict import INTERVAL_INFO_DICT, get_dissonance_score

class MelodyAnalyzer:
    """
    メロディ音とコード構成音の物理的（周波数比）および理論的（機能和声）な整合性を解析するクラス
    """
    def analyze_melody(self, melody_note: Note, chord_root_pc: int, chord_quality: str, chord_notes: List[Note]) -> str:
        lines = [f"Melody: [ {melody_note} ]  vs  Chord: {chord_quality} (Root PC: {chord_root_pc})", "-"*40]
        
        melody_pc = melody_note.pitch_class
        root_diff = (melody_pc - chord_root_pc) % 12
        is_dominant = "7" in chord_quality and "Maj" not in chord_quality and "m7" not in chord_quality
        
        # --- 1. 理論的アヴォイド判定（音楽理論のルール） ---
        theory_avoid = False
        avoid_reason = ""
        
        if root_diff == 5 and ("Maj" in chord_quality or chord_quality == "Major"):
            theory_avoid = True
            avoid_reason = "メジャーコードに対する完全4度 (P4) の衝突"
        elif root_diff == 8 and ("m" in chord_quality and "m7b5" not in chord_quality):
            theory_avoid = True
            avoid_reason = "マイナーコードに対する短6度 (b13) の衝突"

        # --- 2. 物理的・音響学的な不協和判定（全構成音とのインターバル総当たり） ---
        total_dissonance = 0
        acoustic_warnings = []
        acoustic_details = []
        
        for cn in chord_notes:
            # 構成音を基準として、メロディ音への音程を計算（メロディが下にある場合はオクターブを上げて計算）
            dummy_mel = Note(melody_note.step, melody_note.alter, melody_note.octave)
            while dummy_mel.absolute_semitone < cn.absolute_semitone:
                dummy_mel.octave += 1
                
            interval_name = get_interval(cn, dummy_mel)
            info = INTERVAL_INFO_DICT.get(interval_name)
            
            if info:
                score = get_dissonance_score(interval_name)
                total_dissonance += score
                ratio_str = f"{info['ratio'][0]}:{info['ratio'][1]}"
                
                detail = f"  - vs {str(cn):<4} : {interval_name:<3} ({info['name']}) [Ratio {ratio_str}]"
                
                # 強い不協和（m2, m9）の検出
                if score >= 5 or interval_name in ['m2', 'm9']:
                    # ドミナントセブンスのb9は例外として許容
                    if is_dominant and cn.pitch_class == chord_root_pc and interval_name in ['m2', 'm9']:
                        detail += " -> ⚠️ 強い不協和 (b9テンションとして許容)"
                    else:
                        detail += " -> 🚫 アヴォイド要因 (激しい不協和)"
                        acoustic_warnings.append(f"{cn.step}音との間に {interval_name} ({ratio_str}) の不協和が発生")
                        
                acoustic_details.append(detail)
            else:
                acoustic_details.append(f"  - vs {str(cn):<4} : {interval_name:<3} (Unknown Ratio)")
                
        # --- 3. 総合判定 ---
        is_chord_tone = any(cn.pitch_class == melody_pc for cn in chord_notes)
        
        if is_chord_tone:
            status = "Chord Tone (コードトーン: 最も安定)"
        elif theory_avoid or len(acoustic_warnings) > 0:
            status = "Avoid Note (アヴォイドノート: 回避推奨)"
        else:
            status = "Available Tension (有効なテンション: 豊かな響き)"
            
        lines.append(f"Status: {status}")
        
        if theory_avoid:
            lines.append(f"Theory Alert: {avoid_reason}")
        if acoustic_warnings:
            lines.append(f"Acoustic Alert: {', '.join(acoustic_warnings)}")
            
        lines.append(f"Total Dissonance Score: {total_dissonance}")
        lines.append("Acoustic Relationships (vs Chord Tones):")
        lines.extend(acoustic_details)
        
        return "\n".join(lines)