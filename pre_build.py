import re
import os
import shutil

rxDiacritics = re.compile('ӕ')
rxDiaPartsStem = re.compile('( stem:)( *[^\r\n]+)')
rxDiaPartsFlex = re.compile('(-flex:)( *[^\r\n]+)')
rxStemVariants = re.compile('[^ |/]+')
rxFlexVariants = re.compile('[^ /]+')


def collect_lemmata():
    lemmata = ''
    lexrules = ''
    derivations = ''
    clitics = ''
    for fname in os.listdir('.'):
        if fname.endswith('.txt') and fname.startswith('oss_lexemes'):
            f = open(fname, 'r', encoding='utf-8-sig')
            lemmata += f.read() + '\n'
            f.close()
        elif fname.endswith('.txt') and fname.startswith('oss_lexrules'):
            f = open(fname, 'r', encoding='utf-8-sig')
            lexrules += f.read() + '\n'
            f.close()
        elif fname.endswith('.txt') and fname.startswith('oss_derivations'):
            f = open(fname, 'r', encoding='utf-8-sig')
            derivations += f.read() + '\n'
            f.close()
        elif fname.endswith('.txt') and fname.startswith('oss_clitics'):
            f = open(fname, 'r', encoding='utf-8-sig')
            clitics += f.read() + '\n'
            f.close()
    lemmataSet = set(re.findall('-lexeme\n(?: [^\r\n]*\n)+', lemmata, flags=re.DOTALL))
    # lemmata = '\n'.join(sorted(list(lemmataSet),
    #                            key=lambda l: (re.search('gramm: *([^\r\n]*)', l).group(1), l)))
    lemmata = '\n'.join(sorted(list(lemmataSet)))
    return lemmata, lexrules, derivations, clitics


def collect_paradigms():
    fIn = open('oss_paradigms.txt', 'r', encoding='utf-8-sig')
    text = fIn.read()
    fIn.close()
    return text


def add_diacriticless(morph):
    """
    Add a wrong variant to a stem or an inflection (with either ае or
    a Latin character instead of the Cyrillic one)
    """
    morph = morph.group(0)
    if rxDiacritics.search(morph) is None:
        return morph
    return morph + '//' + rxDiacritics.sub('ае', morph) + '//' + rxDiacritics.sub('æ', morph)


def process_diacritics_stem(line):
    """
    Remove diacritics from one line that contains stems.
    """
    morphCorrected = rxStemVariants.sub(add_diacriticless, line.group(2))
    return line.group(1) + morphCorrected


def process_diacritics_flex(line):
    """
    Remove diacritics from one line that contains inflections.
    """
    morphCorrected = rxFlexVariants.sub(add_diacriticless, line.group(2))
    return line.group(1) + morphCorrected


def simplify(text):
    """
    Add diacriticless variants for stems and inflections.
    """
    text = rxDiaPartsStem.sub(process_diacritics_stem, text)
    text = rxDiaPartsFlex.sub(process_diacritics_flex, text)
    return text


def prepare_files():
    """
    Put all the lemmata to lexemes.txt. Put all the lexical
    rules to lexical_rules.txt. Put all the derivations to
    derivations.txt. Create separate versions of
    relevant files for diacriticless texts.
    Put all grammar files to uniparser_ossetic/data_strict/
    (original version) or uniparser_ossetic/data_nodiacritics/
    (diacriticless version).
    """
    lemmata, lexrules, derivations, clitics = collect_lemmata()
    paradigms = collect_paradigms()
    with open('uniparser_ossetic/data_strict/lexemes.txt', 'w', encoding='utf-8') as fOutLemmata:
        fOutLemmata.write(lemmata)
    with open('uniparser_ossetic/data_nodiacritics/lexemes.txt', 'w', encoding='utf-8') as fOutLemmataNodiacritics:
        fOutLemmataNodiacritics.write(simplify(lemmata))
    if len(lexrules) > 0:
        with open('uniparser_ossetic/data_strict/lex_rules.txt', 'w', encoding='utf-8') as fOutLexrules:
            fOutLexrules.write(lexrules)
        with open('uniparser_ossetic/data_nodiacritics/lex_rules.txt', 'w', encoding='utf-8') as fOutLexrules:
            fOutLexrules.write(lexrules)
    with open('uniparser_ossetic/data_strict/paradigms.txt', 'w', encoding='utf-8') as fOutParadigms:
        fOutParadigms.write(paradigms)
    with open('uniparser_ossetic/data_nodiacritics/paradigms.txt', 'w', encoding='utf-8') as fOutParadigmsNodiacritics:
        fOutParadigmsNodiacritics.write(simplify(paradigms))
    with open('uniparser_ossetic/data_strict/derivations.txt', 'w', encoding='utf-8') as fOutDerivations:
        fOutDerivations.write(derivations)
    with open('uniparser_ossetic/data_nodiacritics/derivations.txt', 'w', encoding='utf-8') as fOutDerivations:
        fOutDerivations.write(derivations)
    with open('uniparser_ossetic/data_strict/clitics.txt', 'w', encoding='utf-8') as fOutClitics:
        fOutClitics.write(clitics)
    with open('uniparser_ossetic/data_nodiacritics/clitics.txt', 'w', encoding='utf-8') as fOutClitics:
        fOutClitics.write(clitics)
    if os.path.exists('bad_analyses.txt'):
        shutil.copy2('bad_analyses.txt', 'uniparser_ossetic/data_strict/')
        shutil.copy2('bad_analyses.txt', 'uniparser_ossetic/data_nodiacritics/')
    if os.path.exists('ossetic_disambiguation.cg3'):
        shutil.copy2('ossetic_disambiguation.cg3', 'uniparser_ossetic/data_strict/')
        shutil.copy2('ossetic_disambiguation.cg3', 'uniparser_ossetic/data_nodiacritics/')


def parse_wordlists():
    """
    Analyze wordlists/wordlist.csv.
    """
    from uniparser_ossetic import OsseticAnalyzer
    a = OsseticAnalyzer(mode='strict')
    a.analyze_wordlist(freqListFile='wordlists/wordlist.csv',
                       parsedFile='wordlists/wordlist_analyzed.txt',
                       unparsedFile='wordlists/wordlist_unanalyzed.txt',
                       verbose=True)


if __name__ == '__main__':
    prepare_files()
    parse_wordlists()
