#!/usr/bin/env python3
"""Scarica il dizionario italiano Hunspell da LibreOffice e genera la word list."""

import urllib.request
import re
import os

DIC_URL = "https://raw.githubusercontent.com/LibreOffice/dictionaries/master/it_IT/it_IT.dic"
OUTPUT = os.path.join(os.path.dirname(__file__), "italian_words.txt")


def download_dictionary():
    print("Scaricamento dizionario italiano da LibreOffice...")
    try:
        with urllib.request.urlopen(DIC_URL, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print(f"Errore download: {e}")
        return False

    lines = raw.split("\n")
    words = set()

    # Prima riga: conteggio parole
    start = 0
    if lines and re.match(r"^\d+$", lines[0].strip()):
        start = 1

    for line in lines[start:]:
        line = line.strip()
        if not line:
            continue
        # Estrai la parola prima dello slash (flag hunspell)
        word = line.split("/")[0].strip().lower()
        if word and word.isalpha() and len(word) > 1:
            words.add(word)

    # Forza alcune parole comuni che potrebbero mancare
    extras = {
        "èna", "è", "né", "sé", "sì", "lì", "là", "più", "giù", "ciò",
        "però", "perché", "poiché", "affinché", "benchè", "cioè", "già",
        "può", "così", "dà", "dì", "fà", "là", "lì", "maggio", "eppure",
        "un", "una", "uno", "il", "la", "i", "le", "gli", "lo",
        "c'è", "c'era", "c'erano", "non", "oggi", "bella", "giornata",
        "dell", "nell", "all", "dall", "sull",
        "dell'", "nell'", "all'", "dall'", "sull'",
    }
    words.update(extras)

    # Salva
    sorted_words = sorted(words)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for w in sorted_words:
            f.write(w + "\n")

    print(f"Dizionario salvato: {len(sorted_words):,} parole in {OUTPUT}")
    return True


if __name__ == "__main__":
    download_dictionary()
