
from .tokenizers import tokenize as lang_tokenize


def has_diff(A, B, lang = "python"):
    
    Atok, Btok = list(lang_tokenize(A, lang)), list(lang_tokenize(B, lang))
    
    if len(Atok) != len(Btok): return True
    
    return any(Atok[i] != Btok[i] for i in range(len(Atok)))


def diff_tokens(A, B, lang = "python"):
    
    Atok, Btok = list(lang_tokenize(A, lang)), list(lang_tokenize(B, lang))
    
    limit = min(len(Atok), len(Btok))
    
    diffs = [(Atok[i], Btok[i]) for i in range(limit) if Atok[i] != Btok[i]]
    
    diffs.extend([(Atok[i], ("[NONE]", "None")) for i in range(limit, len(Atok))])
    diffs.extend([(("[NONE]", "None"), Btok[i]) for i in range(limit, len(Btok))])
    
    return diffs
