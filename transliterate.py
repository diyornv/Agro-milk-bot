def latin_to_cyrillic(text: str) -> str:
    mapping = {
        "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ",
        "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
        "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
        "x": "х", "y": "й", "z": "з", "o'": "ў", "g'": "ғ", "sh": "ш", "ch": "ч",
        "ng": "нг", "A": "А", "B": "Б", "D": "Д", "E": "Е", "F": "Ф", "G": "Г",
        "H": "Ҳ", "I": "И", "J": "Ж", "K": "К", "L": "Л", "M": "М", "N": "Н",
        "O": "О", "P": "П", "Q": "Қ", "R": "Р", "S": "С", "T": "Т", "U": "У",
        "V": "В", "X": "Х", "Y": "Й", "Z": "З", "O'": "Ў", "G'": "Ғ", "Sh": "Ш",
        "Ch": "Ч", "Ng": "Нг", "'": "ъ"
    }
    
    # Handle composite characters first to avoid partial replacements
    composites = ["Sh", "sh", "Ch", "ch", "Ng", "ng", "O'", "o'", "G'", "g'"]
    
    result = text
    for comp in composites:
        if comp in mapping:
            result = result.replace(comp, mapping[comp])
            
    for char, cyr in mapping.items():
        if char not in composites:
            result = result.replace(char, cyr)
            
    return result
