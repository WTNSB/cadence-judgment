# dictionaries/cadence_dict.py

CADENCE_DICT = [
    # ==========================================
    # 1. 固有（Diatonic）および強進行系
    # ==========================================
    {
        "from_degree": "V", "from_quality": ["7", "9", "11", "13", "aug7", "dim7"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7", "m9", "m11"],
        "name": "正格終止 (Authentic Cadence): ドミナントから主和音への強進行解決",
        "bonus": 30
    },
    {
        "from_degree": "V", "from_quality": ["7", "9", "11", "13", "aug7", "sus4"],
        "to_degree": "VI", "to_quality_include": ["m", "m7", "m9"],
        "name": "偽終止 (Deceptive Cadence): V7からVImへの期待裏切り進行",
        "bonus": 20
    },
    {
        "from_degree": "II", "from_quality": ["m", "m7", "m9", "m11", "m7b5"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "dim7", "sus4"],
        "name": "ツーファイブ (II-V Progression): ドミナントへの準備進行",
        "bonus": 25
    },
    {
        "from_degree": "IV", "from_quality": ["", "Major", "Maj7", "6", "add9", "Maj9"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "アーメン終止 (Plagal Cadence): サブドミナントから主和音への解決",
        "bonus": 15
    },
    {
        "from_degree": "III", "from_quality": ["m", "m7", "7"],
        "to_degree": "IV", "to_quality_exclude": ["m", "m7"],
        "name": "感情の高揚 (IIIm -> IV): ドミナントを介さないせり上がり",
        "bonus": 15
    },
    {
        "from_degree": "VI", "from_quality": ["m", "m7", "m9"],
        "to_degree": "IV", "to_quality_exclude": ["m", "m7"],
        "name": "切なさを維持した展開 (VIm -> IV): トニック代理からのサブドミナント進行",
        "bonus": 10
    },

    # ==========================================
    # 2. 借用和音 (Modal Interchange / 準固有和音)
    # ==========================================
    {
        "from_degree": "IV", "from_quality": ["m", "m7", "m6", "mM7", "m9"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(エオリアン)からの借用: サブドミナントマイナー終止 (IVm -> I)",
        "bonus": 25
    },
    {
        "from_degree": "bVII", "from_quality": ["7", "9", "11", "13"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(ミクソリディアン)からの借用: バックドア解決 (bVII7 -> I)",
        "bonus": 25
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7", "6", "add9"],
        "to_degree": "bVII", "to_quality_include": ["", "7", "Major", "Maj7", "9"],
        "name": "同主短調(エオリアン)からの借用: エオリアン・カデンツ (bVI -> bVII)",
        "bonus": 20
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7", "6"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(エオリアン)からの借用: 偽終止的着地 (bVI -> I)",
        "bonus": 20
    },
    {
        "from_degree": "bVII", "from_quality": ["", "Major", "Maj7", "7", "9"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "sus4"],
        "name": "同主短調(ミクソリディアン)からの借用: ドミナントへのえぐい回帰 (bVII -> V)",
        "bonus": 25 
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7", "6", "add9"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "sus4"],
        "name": "同主短調(エオリアン)からの借用: 半音下行ドミナントアプローチ (bVI -> V)",
        "bonus": 20
    },
    {
        "from_degree": "IV", "from_quality": ["7", "9", "13"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(ドリアン)からの借用: IV7解決 (IV7 -> I)",
        "bonus": 20
    },

    # ==========================================
    # 3. 代理和音 (Substitutions) および特殊解決
    # ==========================================
    {
        "from_degree": "bII", "from_quality": ["7", "9", "11", "13", "7(#11)"],
        "to_degree": "I", "to_quality_exclude": [],
        "name": "裏コード(Tritone Substitution)による半音下行解決 (bII7 -> I)",
        "bonus": 30
    },
    {
        "from_degree": "III", "from_quality": ["7", "9", "11", "13", "aug7"],
        "to_degree": "VI", "to_quality_include": ["m", "m7", "m9"],
        "name": "セカンダリードミナント: III7によるVImへの強進行解決",
        "bonus": 25
    },
    {
        "from_degree": "IV", "from_quality": ["", "Major", "Maj7"],
        "to_degree": "III", "to_quality_include": ["7", "9", "aug7"],
        "name": "4-3-6-2進行の起点: SD(IV)からセカンダリードミナント(III7)への接続",
        "bonus": 20
    },
    {
        "from_degree": "I", "from_quality": ["", "Major", "Maj7", "6", "add9"],
        "to_degree": "III", "to_quality_include": ["m", "m7"],
        "name": "トニック代理への接続 (I -> IIIm)",
        "bonus": 10
    },
    {
        "from_degree": "IV", "from_quality": ["", "Major", "Maj7", "6", "add9"],
        "to_degree": "II", "to_quality_include": ["m", "m7"],
        "name": "サブドミナント代理への接続 (IV -> IIm)",
        "bonus": 10
    },
    {
        "from_degree": "VI", "from_quality": ["m", "m7", "m9"],
        "to_degree": "III", "to_quality_include": ["m", "m7"],
        "name": "トニック代理(VIm)からドミナント代理(IIIm)への弱進行 (6 -> 3)",
        "bonus": 15
    },

    # ==========================================
    # 4. パッシング・ディミニッシュ (Passing Diminished) 系
    # ==========================================
    {
        "from_degree": "#IV", "from_quality": ["dim", "dim7"],
        "to_degree": "V", "to_quality_exclude": [],
        "name": "パッシング・ディミニッシュ: ベース半音上行アプローチ (#IVdim -> V)",
        "bonus": 20
    },
    {
        "from_degree": "#I", "from_quality": ["dim", "dim7"],
        "to_degree": "II", "to_quality_exclude": [],
        "name": "パッシング・ディミニッシュ: ベース半音上行アプローチ (#Idim -> II)",
        "bonus": 20
    },
    {
        "from_degree": "#V", "from_quality": ["dim", "dim7"],
        "to_degree": "VI", "to_quality_include": ["m", "m7", "m9"],
        "name": "パッシング・ディミニッシュ: ベース半音上行アプローチ (#Vdim -> VIm)",
        "bonus": 20
    }
]