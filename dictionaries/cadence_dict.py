# dictionaries/cadence_dict.py

CADENCE_DICT = [
    # --- ドミナント終止系 ---
    {
        "from_degree": "V", "from_quality": ["7", "9", "11", "13", "aug7", "dim7"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7", "m9", "m11"], # メジャーへの解決
        "name": "ドミナント終止 (Authentic Cadence)",
        "bonus": 30
    },
    {
        "from_degree": "V", "from_quality": ["7", "9", "11", "13", "aug7", "dim7"],
        "to_degree": "VI", "to_quality_include": ["m", "m7", "m9"],
        "name": "偽終止 (Deceptive Cadence)",
        "bonus": 20
    },

    # --- ツーファイブ ---
    {
        "from_degree": "II", "from_quality": ["m", "m7", "m9", "m11", "m7b5"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "dim7", "sus4"],
        "name": "ツーファイブ (II-V Progression)",
        "bonus": 25
    },

    # --- サブドミナント終止系 ---
    {
        "from_degree": "IV", "from_quality": ["", "Major", "Maj7", "6", "add9", "Maj9"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "アーメン終止 (Plagal Cadence)",
        "bonus": 15
    },
    {
        "from_degree": "IV", "from_quality": ["m", "m7", "m6", "mM7", "m9"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "サブドミナントマイナー終止 (Minor Plagal Cadence)",
        "bonus": 25
    },

    # --- セカンダリードミナント・裏コード系 ---
    {
        "from_degree": "bII", "from_quality": ["7", "9", "11", "13", "7(#11)"],
        "to_degree": "I", "to_quality_exclude": [],
        "name": "裏コードからの半音解決 (Tritone Substitution)",
        "bonus": 25
    },
    {
        "from_degree": "III", "from_quality": ["7", "9", "11", "13", "aug7"],
        "to_degree": "VI", "to_quality_include": ["m", "m7", "m9"],
        "name": "セカンダリードミナント (III7 -> VIm)",
        "bonus": 25
    },
    # --- サブドミナントマイナー・特殊解決系 ---
    {
        "from_degree": "bVII", "from_quality": ["7", "9", "11", "13"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "バックドア解決 (Backdoor Progression)",
        "bonus": 25
    },
    {
        "from_degree": "bVII", "from_quality": ["", "Major", "Maj7", "7", "9"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "sus4"],
        "name": "フラットセブンスからのドミナント準備 (bVII -> V)",
        "bonus": 20
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7", "6", "add9"],
        "to_degree": "V", "to_quality_include": ["7", "9", "11", "13", "aug7", "sus4"],
        "name": "サブドミナントマイナーからの半音下行 (bVI -> V)",
        "bonus": 20
    },

    # --- パッシング・ディミニッシュ系 ---
    {
        "from_degree": "#IV", "from_quality": ["dim", "dim7"],
        "to_degree": "V", "to_quality_exclude": [],
        "name": "パッシング・ディミニッシュ (#IVdim -> V)",
        "bonus": 20
    },
    {
        "from_degree": "#I", "from_quality": ["dim", "dim7"],
        "to_degree": "II", "to_quality_exclude": [],
        "name": "パッシング・ディミニッシュ (#Idim -> II)",
        "bonus": 20
    },

    # --- 代理コード・分数aug系 ---
    {
        "from_degree": "IV", "from_quality": ["", "Major", "Maj7"],
        "to_degree": "III", "to_quality_include": ["7", "9", "aug7"],
        "name": "Just the Two of Us進行の入り (IV -> III7)",
        "bonus": 20
    },
    {
        "from_degree": "VI", "from_quality": ["m", "m7", "m9"],
        "to_degree": "III", "to_quality_include": ["m", "m7"],
        "name": "トニック代理への着地 (VIm -> IIIm)",
        "bonus": 15
    },

    # --- 3 -> 4 (ドミナントを介さない上昇) ---
    {
        "from_degree": "III", "from_quality": ["m", "m7", "7"],
        "to_degree": "IV", "to_quality_exclude": [],
        "name": "感情の高揚 (IIIm -> IV)",
        "bonus": 15
    },

    # --- 6 -> 4 (トニックからのサブドミナント進行) ---
    {
        "from_degree": "VI", "from_quality": ["m", "m7"],
        "to_degree": "IV", "to_quality_exclude": [],
        "name": "切なさを維持した展開 (VIm -> IV)",
        "bonus": 10
    },

    # ==========================================
    # 借用和音 (Modal Interchange) 系
    # ==========================================
    {
        "from_degree": "IV", "from_quality": ["m", "m7", "m6", "mM7", "m9"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(エオリアン)からの借用: サブドミナントマイナー終止 (IVm -> I)",
        "bonus": 25
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7"],
        "to_degree": "bVII", "to_quality_exclude": [],
        "name": "同主短調(エオリアン)からの借用: エオリアン・カデンツ (bVI -> bVII)",
        "bonus": 20
    },
    {
        "from_degree": "bVI", "from_quality": ["", "Major", "Maj7"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(エオリアン)からの借用: 偽終止的着地 (bVI -> I)",
        "bonus": 20
    },
    {
        "from_degree": "bVII", "from_quality": ["7", "9", "11", "13"],
        "to_degree": "I", "to_quality_exclude": ["m", "m7"],
        "name": "同主短調(ミクソリディアン)からの借用: バックドア解決 (bVII7 -> I)",
        "bonus": 25
    },

    # ==========================================
    # 代理和音 (Substitutions) 系
    # ==========================================
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
    }
    
]