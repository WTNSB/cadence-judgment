from typing import List, Dict, Any, Set
from models.note import Note
from utils.interval_calc import get_interval
from dictionaries.chord_dict import CHORD_DICT
from engine.fallback_generator import RuleBasedGenerator
from utils.formatter import KeyContext

class ChordAnalyzer:
    def __init__(self):
        self.chord_dictionary = CHORD_DICT

    def analyze(self, notes: List[Note], key: str = "C", threshold: int = 40) -> str:
        if not notes: return "No notes"

        # KeyContextの初期化
        key_context = KeyContext(key)

        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        bass_note = sorted_notes[0]
        
        # ★ 旧コード（bass_alter_str = ... など）を削除し、KeyContextに任せる
        bass_name = key_context.get_note_name(bass_note.pitch_class)

        spread = sorted_notes[-1].absolute_semitone - sorted_notes[0].absolute_semitone
        voicing_type = "Open" if spread > 12 else "Closed"

        input_pcs = {n.pitch_class for n in sorted_notes}
        unique_cands = {n.pitch_class: n for n in sorted_notes}

        categorized_results = {
            "基本形 (Root Position)": [],
            "転回形 (Inversion)": [],
            "オンコード (On-Chord)": [],
            "ルートレス (Rootless)": [],
            "特殊形 (Special)": []
        }

        # 各探索フェーズの実行（今後フェーズが増えたらここに足す）
        self._search_normal(sorted_notes, unique_cands, bass_note, bass_name, voicing_type, categorized_results, key_context)
        self._search_rootless(sorted_notes, input_pcs, bass_note, bass_name, voicing_type, categorized_results, key_context)
        self._search_ust_and_polychord(sorted_notes, unique_cands, input_pcs, bass_note, bass_name, voicing_type, categorized_results, key_context)
        self._search_fallback_rulebased(sorted_notes, unique_cands, bass_note, bass_name, voicing_type, categorized_results, key_context)
        return self._format_output(sorted_notes, bass_name, categorized_results, threshold)
    
    def _search_fallback_rulebased(self, sorted_notes: List[Note], unique_cands: dict, bass_note: Note, bass_name: str, voicing_type: str, results: dict, key_context: KeyContext):
        """辞書にないテンションの組み合わせを動的生成する"""
        for root_pc, cand in unique_cands.items():
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = {get_interval(dummy_root, note) for note in sorted_notes}
            cand_alter_str = "#" if cand.alter == 1 else "b" if cand.alter == -1 else ""
            root_name = f"{cand.step}{cand_alter_str}"
            is_root_pos = (root_pc == bass_note.pitch_class)

            if self.chord_dictionary.get(frozenset(intervals)):
                continue
            
            intervals_with_p5 = set(intervals)
            intervals_with_p5.add('P5')
            if 'P5' not in intervals and self.chord_dictionary.get(frozenset(intervals_with_p5)):
                continue

            # ★ 変更点：複数の解釈（表記ブレ）をリストで受け取る
            generated_qualities = RuleBasedGenerator.generate_chord_names(intervals)
            
            for generated_quality in generated_qualities:
                # テンションが含まれている、または特殊な表記の場合
                if "(" in generated_quality or "aug" in generated_quality:
                    category = self._get_category(is_root_pos, False, generated_quality, root_pc, bass_note)
                    
                    score = 55 if is_root_pos else 35 
                    tension_count = generated_quality.count(',') + 1 if "(" in generated_quality and "omit5" not in generated_quality else 0
                    score += tension_count * 5

                    name = f"{root_name} {generated_quality}" if is_root_pos else f"{root_name} {generated_quality} / {bass_name}"
                    
                    if not any(r['name'].startswith(name) for r in results[category]):
                        results[category].append({"name": f"{name} ({voicing_type}) [生成]", "score": score})

    def _search_ust_and_polychord(self, sorted_notes: List[Note], unique_cands: Dict[int, Note], input_pcs: Set[int], bass_note: Note, bass_name: str, voicing_type: str, results: Dict, key_context: KeyContext):
        """アッパーストラクチャートライアド（UST）およびポリコードの分割探索"""
        if len(input_pcs) < 4:
            return

        triads = {
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Aug": [0, 4, 8],
            "Dim": [0, 3, 6]
        }

        bottom_root_pc = bass_note.pitch_class
        bottom_cand = unique_cands.get(bottom_root_pc)
        if not bottom_cand:
            return

        bottom_dummy_root = Note(bottom_cand.step, bottom_cand.alter, bass_note.octave)
        if bottom_dummy_root.absolute_semitone > bass_note.absolute_semitone:
            bottom_dummy_root.octave -= 1

        for top_pc, top_cand in unique_cands.items():
            if top_pc == bottom_root_pc:
                continue 

            for triad_name, intervals_semi in triads.items():
                top_triad_pcs = {(top_pc + i) % 12 for i in intervals_semi}
                
                if top_triad_pcs.issubset(input_pcs):
                    bottom_pcs = input_pcs - top_triad_pcs
                    bottom_pcs.add(bottom_root_pc) 

                    bottom_intervals = set()
                    for pc in bottom_pcs:
                        note_for_interval = next((n for n in sorted_notes if n.pitch_class == pc), None)
                        if note_for_interval:
                            interval = get_interval(bottom_dummy_root, note_for_interval)
                            if interval[1:] in ['9', '11', '13']:
                                interval = f"{interval[0]}{int(interval[1:]) - 7}"
                            bottom_intervals.add(interval)

                    has_M3 = 'M3' in bottom_intervals
                    has_m3 = 'm3' in bottom_intervals
                    has_m7 = 'm7' in bottom_intervals
                    has_M7 = 'M7' in bottom_intervals

                    bottom_quality = None
                    if has_M3 and has_m7: bottom_quality = "7"
                    elif has_m3 and has_m7: bottom_quality = "m7"
                    elif has_M3 and has_M7: bottom_quality = "Maj7"
                    elif has_m3 and 'd5' in bottom_intervals and has_m7: bottom_quality = "m7b5"
                    elif has_M3: bottom_quality = "" # Major
                    elif has_m3: bottom_quality = "m"

                    if bottom_quality is not None:
                        # --- ★ 変更点: KeyContext を使ってフォーマットする ---
                        top_name = key_context.get_note_name(top_pc)
                        top_chord_name = top_name if triad_name == "Major" else f"{top_name} {triad_name}"

                        bottom_name = key_context.get_note_name(bottom_root_pc)

                        ust_name = f"{top_chord_name} / {bottom_name}{bottom_quality}"
                        
                        root_diff = (top_pc - bottom_root_pc) % 12
                        score = 70 
                        
                        if root_diff in [2, 3, 6, 9] and triad_name in ["Major", "Minor"]:
                            score += 15 
                            
                        if triad_name in ["Aug", "Dim"]:
                            score -= 10 
                        
                        if not any(r['name'].startswith(ust_name) for r in results["特殊形 (Special)"]):
                            results["特殊形 (Special)"].append({"name": f"{ust_name} (UST) ({voicing_type})", "score": score})

    def _calculate_inversion_penalty(self, bass_interval: int) -> int:
        """
        ベース音のインターバルから、転回形やオンコードの不安定さをペナルティとして返す
        """
        if bass_interval in [3, 4]:     # m3, M3 (第1転回形: 比較的安定)
            return 5
        elif bass_interval == 7:        # P5 (第2転回形: 響きは良いが機能が少し曖昧になる)
            return 10
        elif bass_interval in [10, 11]: # m7, M7 (第3転回形: 不安定、強い進行感を求める)
            return 15
        elif bass_interval in [6, 8]:   # d5, A5 (オルタードなベース音: かなり不安定)
            return 15
        else:                           # それ以外のテンションなど（オンコード）
            return 20
    def _get_category(self, is_root_position: bool, is_rootless: bool, quality: str, dummy_root_pc: int, bass_note: Note) -> str:
        if any(sq in quality for sq in ["Quartal", "Quintal", "+6", "Cluster"]):
            return "特殊形 (Special)"
        if is_rootless:
            return "ルートレス (Rootless)"
        if is_root_position:
            return "基本形 (Root Position)"
            
        bass_interval = (bass_note.pitch_class - dummy_root_pc) % 12
        chord_tone_intervals = {3, 4, 6, 7, 8, 10, 11}
        if bass_interval in chord_tone_intervals:
            return "転回形 (Inversion)"
        else:
            return "オンコード (On-Chord)"

    def _search_normal(self, sorted_notes: List[Note], unique_cands: Dict[int, Note], bass_note: Note, bass_name: str, voicing_type: str, results: Dict, key_context: KeyContext):
        for root_pc, cand in unique_cands.items():
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = {get_interval(dummy_root, note) for note in sorted_notes}
            root_name = key_context.get_note_name(root_pc)
            is_root_pos = (root_pc == bass_note.pitch_class)
            
            # A. 完全一致
            quality = self.chord_dictionary.get(frozenset(intervals))
            if quality:
                category = self._get_category(is_root_pos, False, quality, root_pc, bass_note)
                
                # スコア計算の精緻化
                if category == "特殊形 (Special)":
                    score = 75 
                elif is_root_pos:
                    score = 80 # 基本形は満点(80)
                else:
                    # 転回形・オンコードはベース音の度数によってペナルティを引く
                    bass_interval = (bass_note.pitch_class - root_pc) % 12
                    score = 80 - self._calculate_inversion_penalty(bass_interval)
                
                if category == "特殊形 (Special)":
                    name = f"{quality} on {bass_name}"
                else:
                    name = f"{root_name} {quality}" if is_root_pos else f"{root_name} {quality} / {bass_name}"
                    
                results[category].append({"name": f"{name} ({voicing_type})", "score": score})
            
            # B. Omit5 補完
            # （※ここでquality_omitを定義する処理が必要でした）
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality_omit = self.chord_dictionary.get(frozenset(intervals_with_p5))
                
                if quality_omit:
                    category = self._get_category(is_root_pos, False, quality_omit, root_pc, bass_note)
                    
                    # スコア計算の精緻化 (Omit5なので基礎点は65)
                    if is_root_pos:
                        score = 65
                    else:
                        bass_interval = (bass_note.pitch_class - root_pc) % 12
                        score = 65 - self._calculate_inversion_penalty(bass_interval)
                        
                    name = f"{root_name} {quality_omit}(omit5)" if is_root_pos else f"{root_name} {quality_omit}(omit5) / {bass_name}"
                    results[category].append({"name": f"{name} ({voicing_type})", "score": score})

    def _search_rootless(self, sorted_notes: List[Note], input_pcs: Set[int], bass_note: Note, bass_name: str, voicing_type: str, results: Dict, key_context: KeyContext):
        missing_pcs = [pc for pc in range(12) if pc not in input_pcs]

        for phantom_pc in missing_pcs:
            phantom_root = Note('C', phantom_pc, bass_note.octave)
            if phantom_root.absolute_semitone > bass_note.absolute_semitone:
                phantom_root.octave -= 1
                
            intervals = {'P1'}
            for note in sorted_notes:
                intervals.add(get_interval(phantom_root, note))
                
            quality = self.chord_dictionary.get(frozenset(intervals))
            is_omit5 = False
            
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality = self.chord_dictionary.get(frozenset(intervals_with_p5))
                if quality: is_omit5 = True

            if quality and any(ext in quality for ext in ['7', '9', '11', '13', 'dim']):
                root_name = key_context.get_note_name(phantom_pc)
                
                tension_bonus = 0
                if '9' in quality: tension_bonus += 10
                if '11' in quality: tension_bonus += 15
                if '13' in quality: tension_bonus += 20
                
                score = 30 + tension_bonus - (10 if is_omit5 else 0)
                omit_str = "(omit5)" if is_omit5 else ""
                name = f"{root_name} {quality}{omit_str}(Rootless) / {bass_name}"
                results["ルートレス (Rootless)"].append({"name": f"{name} ({voicing_type})", "score": score})

    def _format_output(self, sorted_notes: List[Note], bass_name: str, categorized_results: Dict, threshold: int) -> str:
        notes_str = ", ".join(str(n) for n in sorted_notes)
        output_lines = [f"Input: [{notes_str}] (Bass: {bass_name})", "-"*40]
        
        has_results = False
        for category, results in categorized_results.items():
            filtered_results = sorted([r for r in results if r['score'] >= threshold], key=lambda x: x['score'], reverse=True)
            
            if filtered_results:
                has_results = True
                output_lines.append(f"■ {category}")
                seen = set()
                for res in filtered_results:
                    if res['name'] not in seen:
                        seen.add(res['name'])
                        output_lines.append(f"  - {res['name']} [Score: {res['score']}]")

        if not has_results:
            output_lines.append(f"Analyzed: Unknown (No interpretation scored above {threshold})")
            
        output_lines.append("-" * 40)
        return "\n".join(output_lines)