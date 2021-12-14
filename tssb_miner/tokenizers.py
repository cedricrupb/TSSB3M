import token
import tokenize

from io import StringIO


# API methods ---------------------------------------------------------------------

def tokenize(text, lang = "python"):

    if lang == "python":
        for tok in pytokenize_text(text): yield tok
        return

    raise ValueError("Unknown language: %s" % lang)


def lang_tokenize(text, lang = "python"):

    for token, token_type in tokenize(text, lang):
        if "comment" in token_type.lower(): continue

        yield (token, token_type)


def iter_stmts(text, lang = "python"):
    
    if lang == "python":
        for stmt in pyiter_stmts(text): yield stmt
        return

    raise ValueError("Unknown language: %s" % lang)


# Python tokenizer ----------------------------------------------------------------

def pytokenize_text(line):

    try:
        for tok in tokenize.generate_tokens(StringIO(line).readline):
            yield (tok.string, token.tok_name[tok.type])
    except Exception:
        yield ("ERROR", "ERROR")


def pyiter_stmts(text): 

    start_ix = 0
    
    brackets = {"{":"}", "(":")", "[":"]"}
    bcount = {b: 0 for b in brackets.values()}
    
    for i, c in enumerate(text):
        if c in brackets and not (c in bcount and bcount[c] > 0): bcount[brackets[c]] += 1 ; continue
        if c in bcount:   bcount[c] -= 1 ; continue
        
        should_split = False
        
        if c == ";": should_split = True
        if c == "\n": should_split = sum(bcount.values()) == 0
        
        if should_split:
            if i != start_ix: yield text[start_ix:i]
            start_ix = i + 1