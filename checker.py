"""
Modulo di analisi ortografica e grammaticale per testi italiani.
Combina:
- Controllo ortografico via dizionario (Levenshtein per suggerimenti)
- Regole grammaticali per errori comuni italiani
"""

import re
import os
from collections import defaultdict


# ---------- Levenshtein distance ----------
def levenshtein(s1: str, s2: str) -> int:
    """Distanza di Levenshtein ottimizzata."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


# ---------- Dizionario italiano ----------
class ItalianDictionary:
    """Gestisce il dizionario italiano per il controllo ortografico."""

    def __init__(self, dict_path: str = None):
        if dict_path is None:
            dict_path = os.path.join(os.path.dirname(__file__), "italian_words.txt")
        self.words: set = set()
        self._load(dict_path)

    def _load(self, path: str):
        # Carica sempre il built-in come base
        self._load_builtin()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        self.words.add(w)

    def _load_builtin(self):
        """Mini-dizionario incorporato (usato se il file non esiste)."""
        builtin = {
            # Articoli
            "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "un'",
            # Preposizioni
            "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
            "del", "dello", "della", "dei", "degli", "delle",
            "al", "allo", "alla", "ai", "agli", "alle",
            "dal", "dallo", "dalla", "dai", "dagli", "dalle",
            "nel", "nello", "nella", "nei", "negli", "nelle",
            "col", "sul", "sullo", "sulla", "sui", "sugli", "sulle",
            # Congiunzioni
            "e", "ed", "o", "ma", "che", "se", "né", "perché", "poiché", "quindi",
            "dunque", "mentre", "quando", "come", "così", "anche", "infatti",
            "invece", "oppure", "ovvero", "cioè", "ossia", "cioè",
            # Pronomi
            "io", "tu", "lui", "lei", "noi", "voi", "loro", "me", "te", "sé",
            "mi", "ti", "si", "ci", "vi", "lo", "la", "li", "le", "ne",
            "mio", "tuo", "suo", "nostro", "vostro", "loro",
            "questo", "quello", "codesto", "ciò", "questi", "quelli",
            "chi", "che", "cui", "quale", "quali",
            # Avverbi comuni
            "non", "sì", "no", "già", "mai", "sempre", "spesso", "mai",
            "bene", "male", "molto", "poco", "tanto", "troppo", "abbastanza",
            "dove", "qui", "qua", "lì", "là", "dovunque", "ovunque",
            "oggi", "ieri", "domani", "ora", "adesso", "prima", "dopo", "poi",
            "presto", "tardi", "ancora", "ormai", "subito",
            "più", "meno", "meglio", "peggio", "così", "così",
            "insieme", "volentieri", "certamente", "davvero", "forse",
            "circa", "almeno", "soprattutto", "soltanto", "pure", "neppure",
            "ecco", "eppure", "piuttosto", "infatti", "inoltre",
            # Verbi comuni (forme base + coniugazioni frequenti)
            "essere", "sono", "sei", "è", "siamo", "siete", "era", "erano",
            "stato", "stata", "stati", "state", "sarà", "saranno", "fosse",
            "avere", "ho", "hai", "ha", "abbiamo", "avete", "hanno",
            "aveva", "avevano", "avuto", "avuta", "avuti", "avrà",
            "fare", "faccio", "fai", "fa", "facciamo", "fate", "fanno",
            "faceva", "fatto", "fatta", "fatti", "farà", "fece", "fecero",
            "dire", "dico", "dici", "dice", "diciamo", "dite", "dicono",
            "detto", "detta", "detti", "dette", "disse", "dissero",
            "andare", "vado", "vai", "va", "andiamo", "andate", "vanno",
            "andava", "andato", "andata", "andrò", "andò", "andarono",
            "venire", "vengo", "vieni", "viene", "veniamo", "venite", "vengono",
            "venuto", "venuta", "venuti", "verrà", "venne", "vennero",
            "potere", "posso", "puoi", "può", "possiamo", "potete", "possono",
            "potuto", "potrà", "potrebbe", "potrebbero",
            "volere", "voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono",
            "voluto", "vorrà", "vorrebbe", "vorrei",
            "dovere", "devo", "devi", "deve", "dobbiamo", "dovete", "devono",
            "dovuto", "dovrà", "dovrebbe", "dovrei",
            "sapere", "so", "sai", "sa", "sappiamo", "sapete", "sanno",
            "saputo", "saprà", "sapeva", "seppe",
            "stare", "sto", "stai", "sta", "stiamo", "state", "stanno",
            "stavo", "starò", "stette", "stettero",
            "vedere", "vedo", "vedi", "vede", "vediamo", "vedete", "vedono",
            "visto", "vista", "visti", "vedrà", "vide", "videro",
            "dare", "do", "dai", "dà", "diamo", "date", "danno",
            "dato", "data", "darà", "diede", "diedero",
            "parlare", "parlo", "parli", "parla", "parliamo", "parlate", "parlano",
            "pensare", "penso", "pensi", "pensa", "pensiamo", "pensate", "pensano",
            "trovare", "trovo", "trovi", "trova", "troviamo", "trovate", "trovano",
            "lasciare", "lascio", "lasci", "lascia", "lasciamo", "lasciate", "lasciano",
            "sentire", "sento", "senti", "sente", "sentiamo", "sentite", "sentono",
            "credere", "credo", "credi", "crede", "crediamo", "credete", "credono",
            "portare", "porto", "porti", "porta", "portiamo", "portate", "portano",
            "mettere", "metto", "metti", "mette", "mettiamo", "mettete", "mettono",
            "vivere", "vivo", "vivi", "vive", "viviamo", "vivete", "vivono",
            "prendere", "prendo", "prendi", "prende", "prendiamo", "prendete", "prendono",
            "capire", "capisco", "capisci", "capisce", "capiamo", "capite", "capiscono",
            "tenere", "tengo", "tieni", "tiene", "teniamo", "tenete", "tengono",
            "uscire", "esco", "esci", "esce", "usciamo", "uscite", "escono",
            "morire", "muoio", "muori", "muore", "moriamo", "morite", "muoiono",
            "rimanere", "rimango", "rimani", "rimane", "rimaniamo", "rimanete", "rimangono",
            "lavorare", "lavoro", "lavori", "lavora", "lavoriamo", "lavorate", "lavorano",
            "amare", "amo", "ami", "ama", "amiamo", "amate", "amano",
            "mangiare", "mangio", "mangi", "mangia", "mangiamo", "mangiate", "mangiano",
            "bere", "bevo", "bevi", "beve", "beviamo", "bevete", "bevono",
            "scrivere", "scrivo", "scrivi", "scrive", "scriviamo", "scrivete", "scrivono",
            "leggere", "leggo", "leggi", "legge", "leggiamo", "leggete", "leggono",
            "finire", "finisco", "finisci", "finisce", "finiamo", "finite", "finiscono",
            "aprire", "apro", "apri", "apre", "apriamo", "aprite", "aprono",
            "chiudere", "chiudo", "chiudi", "chiude", "chiudiamo", "chiudete", "chiudono",
            "correre", "corro", "corri", "corre", "corriamo", "correte", "corrono",
            "ridere", "rido", "ridi", "ride", "ridiamo", "ridete", "ridono",
            "piacere", "piaccio", "piaci", "piace", "piacciamo", "piacete", "piacciono",
            "chiamare", "chiamo", "chiami", "chiama", "chiamiamo", "chiamate", "chiamano",
            "entrare", "entro", "entri", "entra", "entriamo", "entrate", "entrano",
            "giocare", "gioco", "giochi", "gioca", "giochiamo", "giocate", "giocano",
            "guardare", "guardo", "guardi", "guarda", "guardiamo", "guardate", "guardano",
            "ascoltare", "ascolto", "ascolti", "ascolta", "ascoltiamo", "ascoltate", "ascoltano",
            "comprare", "compro", "compri", "compra", "compriamo", "comprate", "comprano",
            "aspettare", "aspetto", "aspetti", "aspetta", "aspettiamo", "aspettate", "aspettano",
            "cambiare", "cambio", "cambi", "cambia", "cambiamo", "cambiate", "cambiano",
            # Aggettivi comuni
            "bello", "bella", "belli", "belle", "bellissimo", "bellissima",
            "buono", "buona", "buoni", "buone", "buonissimo",
            "grande", "grandi", "piccolo", "piccola", "piccoli", "piccole",
            "nuovo", "nuova", "nuovi", "nuove",
            "vecchio", "vecchia", "vecchi", "vecchie",
            "giovane", "giovani",
            "alto", "alta", "alti", "alte",
            "basso", "bassa", "bassi", "basse",
            "lungo", "lunga", "lunghi", "lunghe",
            "corto", "corta", "corti", "corte",
            "bianco", "bianca", "bianchi", "bianche",
            "nero", "nera", "neri", "nere",
            "rosso", "rossa", "rossi", "rosse",
            "verde", "verdi",
            "blu", "giallo", "gialla", "gialli", "gialle",
            "caldo", "calda", "caldi", "calde",
            "freddo", "fredda", "freddi", "fredde",
            "forte", "forti", "debole", "deboli",
            "felice", "felici", "triste", "tristi",
            "contento", "contenta", "contenti", "contente",
            "facile", "facili", "difficile", "difficili",
            "veloce", "veloci", "lento", "lenta", "lenti", "lente",
            "importante", "importanti",
            "diverso", "diversa", "diversi", "diverse",
            "stesso", "stessa", "stessi", "stesse",
            "vero", "vera", "veri", "vere",
            "primo", "prima", "primi", "prime",
            "ultimo", "ultima", "ultimi", "ultime",
            "solo", "sola", "soli", "sole",
            "pieno", "piena", "pieni", "piene",
            "vuoto", "vuota", "vuoti", "vuote",
            "povero", "povera", "poveri", "povere",
            "ricco", "ricca", "ricchi", "ricche",
            "bravo", "brava", "bravi", "brave",
            "carino", "carina", "carini", "carine",
            # Nomi comuni
            "cosa", "cose", "oggetto", "oggetti",
            "persona", "persone", "uomo", "uomini", "donna", "donne",
            "bambino", "bambina", "bambini", "bambine",
            "ragazzo", "ragazza", "ragazzi", "ragazze",
            "signore", "signora", "signori", "signore",
            "amico", "amica", "amici", "amiche",
            "padre", "padri", "madre", "madri",
            "fratello", "fratelli", "sorella", "sorelle",
            "figlio", "figlia", "figli", "figlie",
            "marito", "moglie", "mariti", "mogli",
            "casa", "case", "porta", "porte",
            "finestra", "finestre", "tetto", "tetti",
            "strada", "strade", "via", "vie",
            "città", "paese", "paesi",
            "mondo", "mondi", "terra", "terre",
            "mare", "mari", "fiume", "fiumi", "lago", "laghi",
            "montagna", "montagne", "monte", "monti",
            "albero", "alberi", "fiore", "fiori",
            "animale", "animali", "cane", "cani", "gatto", "gatti",
            "uccello", "uccelli", "pesce", "pesci",
            "cibo", "cibi", "pane", "vino", "acqua", "latte",
            "tempo", "tempi", "giorno", "giorni", "giornata", "giornate",
            "notte", "notti", "sera", "sere", "mattina", "mattine",
            "anno", "anni", "mese", "mesi", "settimana", "settimane",
            "ora", "ore", "minuto", "minuti", "secondo", "secondi",
            "vita", "vite", "morte", "amore", "amori",
            "lavoro", "lavori", "scuola", "scuole",
            "libro", "libri", "storia", "storie",
            "parola", "parole", "frase", "frasi",
            "testa", "teste", "mano", "mani", "piede", "piedi",
            "occhio", "occhi", "orecchio", "orecchie",
            "cuore", "cuori", "mente", "menti",
            "corpo", "corpi", "anima", "anime",
            "voce", "voci", "suono", "suoni",
            "luce", "luci", "ombra", "ombre",
            "colore", "colori", "odore", "odori",
            "nome", "nomi", "numero", "numeri",
            "soldi", "denaro", "prezzo", "prezzi",
            "guerra", "guerre", "pace",
            "forza", "forze", "energia", "energie",
            "problema", "problemi", "soluzione", "soluzioni",
            "idea", "idee", "pensiero", "pensieri",
            "domanda", "domande", "risposta", "risposte",
            "errore", "errori", "sbaglio", "sbagli",
            "esempio", "esempi", "modo", "modi",
            "volta", "volte", "parte", "parti",
            "fine", "inizio", "inizi",
            "diritto", "diritti", "dovere", "doveri",
            "politica", "politiche", "governo", "governi",
            "arte", "arti", "musica", "musiche",
            "film", "cinema",
            "macchina", "macchine", "auto", "automobile", "automobili",
            "telefono", "telefoni", "computer",
            "stazione", "stazioni", "treno", "treni",
            "ospedale", "ospedali", "medico", "medici",
            "chiesa", "chiese", "piazza", "piazze",
            "albergo", "alberghi", "ristorante", "ristoranti",
            "bicchiere", "bicchieri", "bottiglia", "bottiglie",
            "tavolo", "tavoli", "sedia", "sedie",
            "letto", "letti", "camera", "camere",
            "bagno", "bagni", "cucina", "cucine",
            "giardino", "giardini", "parco", "parchi",
            "festa", "feste", "regalo", "regali",
            "notizia", "notizie", "informazione", "informazioni",
            "aiuto", "aiuti", "bisogno", "bisogni",
            "risultato", "risultati", "successo", "successi",
            "memoria", "memorie", "sogno", "sogni",
            # --- Supplemento: parole comuni mancanti nel dizionario Hunspell ---
            "nome", "nomi", "cognome", "cognomi",
            "parola", "parole", "frase", "frasi", "testo", "testi",
            "italiano", "italiana", "italiani", "italiane",
            "inglese", "francese", "tedesco", "spagnolo",
            "lingua", "lingue", "linguaggio", "linguaggi",
            "grammatica", "grammatiche", "ortografia",
            "vocale", "vocali", "consonante", "consonanti",
            "accento", "accenti", "apostrofo", "apostrofi",
            "punteggiatura", "virgola", "virgole", "punto", "punti",
            "sillaba", "sillabe", "alfabeto", "alfabeti",
            "dizionario", "dizionari", "vocabolario",
            "significato", "significati", "sinonimo", "sinonimi",
            "contrario", "contrari", "definizione", "definizioni",
            "lezione", "lezioni", "esercizio", "esercizi",
            "compito", "compiti", "verifica", "verifiche",
            "interrogazione", "professore", "professoressa",
            "maestro", "maestra", "alunno", "alunna", "alunni", "alunne",
            "studente", "studentessa", "studenti", "studentesse",
            "università", "facoltà", "corso", "corsi",
            "laurea", "lauree", "dottore", "dottoressa",
            "ingegnere", "architetto", "avvocato", "avvocati",
            "giudice", "giudici", "poliziotto", "poliziotti",
            "carabiniere", "carabinieri", "soldato", "soldati",
            "papa", "papi", "vescovo", "vescovi", "prete", "preti",
            "santo", "santa", "santi", "sante", "dio", "dei",
            "angelo", "angeli", "diavolo", "diavoli",
            "paradiso", "inferno", "purgatorio",
            "sole", "soli", "luna", "lune", "stella", "stelle",
            "cielo", "cieli", "nuvola", "nuvole", "pioggia", "piogge",
            "neve", "nevi", "vento", "venti", "tempesta", "tempeste",
            "fulmine", "fulmini", "tuono", "tuoni",
            "arcobaleno", "arcobaleni", "orizzonte", "orizzonti",
            "natura", "paesaggio", "paesaggi", "ambiente", "ambienti",
            "inquinamento", "ecologia", "clima", "climi",
            "animale", "animali", "pianta", "piante",
            "foresta", "foreste", "deserto", "deserti",
            "isola", "isole", "penisola", "penisole",
            "continente", "continenti", "oceano", "oceani",
            "nord", "sud", "est", "ovest",
            "europa", "italia", "francia", "germania", "spagna",
            "roma", "milano", "napoli", "torino", "firenze",
            "venezia", "palermo", "bologna", "genova", "bari",
            "colosseo", "pantheon", "duomo", "basilica",
            "museo", "musei", "galleria", "gallerie",
            "mostra", "mostre", "concerto", "concerti",
            "teatro", "teatri", "spettacolo", "spettacoli",
            "attore", "attrice", "attori", "attrici",
            "regista", "registi", "sceneggiatore", "sceneggiatori",
            "romanzo", "romanzi", "racconto", "racconti",
            "poesia", "poesie", "poeta", "poeti", "poetessa",
            "autore", "autrice", "autori", "autrici",
            "editore", "editori", "giornale", "giornali",
            "rivista", "riviste", "articolo", "articoli",
            "giornalista", "giornalisti", "cronaca", "cronache",
            "intervista", "interviste", "inchiesta", "inchieste",
            "televisione", "radio", "canale", "canali",
            "programma", "programmi", "trasmissione", "trasmissioni",
            "pubblicità", "annuncio", "annunci",
            "internet", "web", "sito", "siti", "pagina", "pagine",
            "social", "network", "email", "messaggio", "messaggi",
            "chat", "video", "foto", "fotografia", "fotografie",
            "immagine", "immagini", "schermo", "schermi",
            "tastiera", "tastiere", "mouse", "stampante", "stampanti",
            "cellulare", "cellulari", "smartphone", "tablet",
            "applicazione", "applicazioni", "software", "hardware",
            "programma", "programmi", "sistema", "sistemi",
            "rete", "reti", "server", "database",
            "password", "account", "profilo", "profili",
            "algoritmo", "algoritmi", "codice", "codici",
            "digitale", "analogico", "virtuale", "reale",
            "tecnologia", "tecnologie", "innovazione", "innovazioni",
            "scienza", "scienze", "scienziato", "scienziati",
            "fisica", "chimica", "biologia", "matematica",
            "storia", "storie", "geografia", "filosofia",
            "psicologia", "sociologia", "economia", "economie",
            "statistica", "statistiche", "ricerca", "ricerche",
            "esperimento", "esperimenti", "laboratorio", "laboratori",
            "teoria", "teorie", "ipotesi", "tesi",
            "dato", "dati", "analisi", "risultato", "risultati",
            "grafico", "grafici", "tabella", "tabelle",
            "formula", "formule", "equazione", "equazioni",
            "cerchio", "cerchi", "quadrato", "quadrati",
            "triangolo", "triangoli", "rettangolo", "rettangoli",
            "linea", "linee", "curva", "curve", "angolo", "angoli",
            "spazio", "spazi", "tempo", "tempi", "velocità",
            "distanza", "distanze", "lunghezza", "lunghezze",
            "larghezza", "larghezze", "altezza", "altezze",
            "profondità", "superficie", "superfici", "volume", "volumi",
            "peso", "pesi", "massa", "masse", "densità",
            "temperatura", "temperature", "pressione", "pressioni",
            "energia", "energie", "potenza", "potenze",
            "elettricità", "elettrico", "elettrica", "elettronici",
            "magnete", "magneti", "campo", "campi", "onda", "onde",
            "atomo", "atomi", "molecola", "molecole",
            "cellula", "cellule", "tessuto", "tessuti",
            "organo", "organi", "organismo", "organismi",
            "specie", "genere", "generi", "famiglia", "famiglie",
            "regno", "regni", "phylum", "classe", "classi",
            "ordine", "ordini", "categoria", "categorie",
            "gruppo", "gruppi", "insieme", "insiemi",
            "elemento", "elementi", "componente", "componenti",
            "fattore", "fattori", "variabile", "variabili",
            "funzione", "funzioni", "processo", "processi",
            "metodo", "metodi", "tecnica", "tecniche",
            "strumento", "strumenti", "attrezzo", "attrezzi",
            "dispositivo", "dispositivi", "meccanismo", "meccanismi",
            "motore", "motori", "veicolo", "veicoli",
            "aeroplano", "aeroplani", "elicottero", "elicotteri",
            "nave", "navi", "barca", "barche", "porto", "porti",
            "aeroporto", "aeroporti", "ferrovia", "ferrovie",
            "autostrada", "autostrade", "galleria", "gallerie",
            "ponte", "ponti", "tunnel", "viadotto", "viadotti",
            "palazzo", "palazzi", "edificio", "edifici",
            "costruzione", "costruzioni", "struttura", "strutture",
            "materiale", "materiali", "metallo", "metalli",
            "ferro", "acciaio", "alluminio", "rame", "oro", "argento",
            "legno", "legni", "pietra", "pietre", "vetro", "vetri",
            "plastica", "plastiche", "gomma", "gomme", "tessuto", "tessuti",
            "cotone", "lana", "seta", "pelle", "pelli",
            "carta", "carte", "cartone", "cartoni",
            "colore", "colori", "vernice", "vernici", "pittura", "pitture",
            "disegno", "disegni", "schizzo", "schizzi", "bozza", "bozze",
            "progetto", "progetti", "piano", "piani", "schema", "schemi",
            "modello", "modelli", "prototipo", "prototipi",
            "brevetto", "brevetti", "invenzione", "invenzioni",
            "scoperta", "scoperte", "creazione", "creazioni",
            "opera", "opere", "capolavoro", "capolavori",
            "quadro", "quadri", "scultura", "sculture",
            "statua", "statue", "monumento", "monumenti",
            "tempio", "templi", "castello", "castelli",
            "fortezza", "fortezze", "mura", "torre", "torri",
            "campanile", "campanili", "campana", "campane",
            "orologio", "orologi", "sveglia", "sveglie",
            "calendario", "calendari", "agenda", "agende",
            "appuntamento", "appuntamenti", "riunione", "riunioni",
            "conferenza", "conferenze", "congresso", "congressi",
            "assemblea", "assemblee", "comitato", "comitati",
            "consiglio", "consigli", "decisione", "decisioni",
            "scelta", "scelte", "opzione", "opzioni",
            "alternativa", "alternative", "opportunità",
            "possibilità", "probabilità", "rischio", "rischi",
            "pericolo", "pericoli", "sicurezza", "sicurezze",
            "protezione", "protezioni", "difesa", "difese",
            "attacco", "attacchi", "conflitto", "conflitti",
            "battaglia", "battaglie", "vittoria", "vittorie",
            "sconfitta", "sconfitte", "pace", "pacifica",
            "accordo", "accordi", "trattato", "trattati",
            "alleanza", "alleanze", "patto", "patti",
            "legge", "leggi", "regola", "regole", "norma", "norme",
            "regolamento", "regolamenti", "costituzione", "costituzioni",
            "decreto", "decreti", "sentenza", "sentenze",
            "processo", "processi", "tribunale", "tribunali",
            "corte", "corti", "carcere", "carceri", "prigione", "prigioni",
            "pena", "pene", "condanna", "condanne", "reato", "reati",
            "crimine", "crimini", "delitto", "delitti",
            "colpa", "colpe", "innocenza", "colpevole", "innocente",
            "testimone", "testimoni", "prova", "prove", "indizio", "indizi",
            "indagine", "indagini", "investigazione", "investigazioni",
            "diritto", "diritti", "dovere", "doveri", "libertà",
            "uguaglianza", "giustizia", "democrazia", "democrazie",
            "dittatura", "dittature", "regime", "regimi",
            "elezione", "elezioni", "voto", "voti", "partito", "partiti",
            "parlamento", "parlamenti", "senato", "senati",
            "presidente", "presidenti", "ministro", "ministri",
            "sindaco", "sindaci", "cittadino", "cittadina", "cittadini",
            "popolo", "popoli", "nazione", "nazioni", "stato", "stati",
            "regione", "regioni", "provincia", "province", "comune", "comuni",
            "territorio", "territori", "confine", "confini",
            "frontiera", "frontiere", "dogana", "dogane",
            "passaporto", "passaporti", "visto", "visti",
            "turista", "turisti", "viaggiatore", "viaggiatori",
            "vacanza", "vacanze", "ferie", "villeggiatura",
            "albergo", "alberghi", "pensione", "pensioni",
            "prenotazione", "prenotazioni", "biglietto", "biglietti",
            "valigia", "valigie", "bagaglio", "bagagli",
            "aereo", "aerei", "volo", "voli", "scalo", "scali",
            "imbarco", "imbarchi", "atterraggio", "atterraggi",
            "passeggero", "passeggeri", "pilota", "piloti",
            "hostess", "steward", "equipaggio", "equipaggi",
            "benzina", "gasolio", "carburante", "carburanti",
            "officina", "officine", "meccanico", "meccanici",
            "riparazione", "riparazioni", "guasto", "guasti",
            "incidente", "incidenti", "scontro", "scontri",
            "traffico", "code", "semaforo", "semafori",
            "incrocio", "incroci", "rotonda", "rotonde",
            "marciapiede", "marciapiedi", "pedone", "pedoni",
            "bicicletta", "biciclette", "motorino", "motorini",
            "moto", "motocicletta", "motociclette", "scooter",
            "camion", "camioncino", "furgone", "furgoni",
            "autobus", "pullman", "tram", "metropolitana", "metropolitane",
            "taxi", "tassista", "tassisti",
            "mercato", "mercati", "supermercato", "supermercati",
            "negozio", "negozi", "boutique", "centro", "centri",
            "commerciale", "commerciali", "vendita", "vendite",
            "acquisto", "acquisti", "spesa", "spese", "scontrino", "scontrini",
            "cassa", "casse", "bancomat", "carta", "contanti",
            "euro", "dollaro", "dollari", "sterlina", "sterline",
            "moneta", "monete", "banconota", "banconote",
            "banca", "banche", "borsa", "borse", "finanza", "finanze",
            "investimento", "investimenti", "risparmio", "risparmi",
            "debito", "debiti", "credito", "crediti", "mutuo", "mutui",
            "prestito", "prestiti", "tasso", "tassi", "interesse", "interessi",
            "inflazione", "crescita", "sviluppo", "recessione",
            "disoccupazione", "occupazione", "lavoratore", "lavoratori",
            "dipendente", "dipendenti", "impiegato", "impiegata", "impiegati",
            "operaio", "operaia", "operai", "operaie",
            "dirigente", "dirigenti", "manager", "amministratore", "amministratori",
            "imprenditore", "imprenditrice", "imprenditori",
            "azienda", "aziende", "impresa", "imprese", "società",
            "fabbrica", "fabbriche", "industria", "industrie",
            "produzione", "produzioni", "prodotto", "prodotti",
            "merce", "merci", "magazzino", "magazzini",
            "fornitore", "fornitori", "cliente", "clienti",
            "consumatore", "consumatori", "utente", "utenti",
            "servizio", "servizi", "qualità", "quantità",
            "prezzo", "prezzi", "costo", "costi", "valore", "valori",
            "offerta", "offerte", "domanda", "domande",
            "contratto", "contratti", "fattura", "fatture",
            "pagamento", "pagamenti", "ricevuta", "ricevute",
            "garanzia", "garanzie", "reclamo", "reclami",
            "rimborso", "rimborsi", "reso", "resi",
            "spedizione", "spedizioni", "consegna", "consegne",
            "pacco", "pacchi", "posta", "poste", "corriere", "corrieri",
            "lettera", "lettere", "busta", "buste", "francobollo", "francobolli",
            "indirizzo", "indirizzi", "destinatario", "destinatari",
            "mittente", "mittenti", "oggetto", "oggetti",
            "salute", "malattia", "malattie", "sintomo", "sintomi",
            "febbre", "tosse", "raffreddore", "raffreddori",
            "influenza", "influenze", "allergia", "allergie",
            "farmaco", "farmaci", "medicina", "medicine",
            "pillola", "pillole", "sciroppo", "sciroppi",
            "iniezione", "iniezioni", "vaccino", "vaccini",
            "terapia", "terapie", "cura", "cure", "trattamento", "trattamenti",
            "chirurgia", "operazione", "operazioni", "intervento", "interventi",
            "pronto", "soccorso", "ambulanza", "ambulanze",
            "analisi", "esame", "esami", "radiografia", "radiografie",
            "ricetta", "ricette", "dieta", "diete", "alimentazione",
            "nutrizione", "vitamina", "vitamine", "proteina", "proteine",
            "carboidrato", "carboidrati", "grasso", "grassi", "fibra", "fibre",
            "colazione", "pranzo", "cena", "merenda", "spuntino", "spuntini",
            "antipasto", "antipasti", "pietanza", "pietanze", "contorno", "contorni",
            "dolce", "dolci", "gelato", "gelati", "torta", "torte",
            "biscotto", "biscotti", "cioccolato", "cioccolati",
            "caramella", "caramelle", "zucchero", "zuccheri", "miele",
            "caffè", "tè", "tisana", "tisane", "succo", "succhi",
            "birra", "birre", "liquore", "liquori", "cocktail",
            "carne", "carni", "pesce", "pesci", "pollo", "polli",
            "manzo", "maiale", "maiali", "agnello", "agnelli",
            "prosciutto", "prosciutti", "salame", "salami",
            "formaggio", "formaggi", "mozzarella", "mozzarelle",
            "parmigiano", "pecorino", "ricotta", "ricotte",
            "pasta", "paste", "spaghetti", "penne", "fusilli",
            "riso", "risi", "risotto", "risotti",
            "pizza", "pizze", "focaccia", "focacce",
            "pomodoro", "pomodori", "insalata", "insalate",
            "verdura", "verdure", "frutta", "frutti",
            "mela", "mele", "pera", "pere", "banana", "banane",
            "arancia", "arance", "limone", "limoni", "fragola", "fragole",
            "ciliegia", "ciliegie", "pesca", "pesche", "albicocca", "albicocche",
            "uva", "uve", "anguria", "angurie", "melone", "meloni",
            "oliva", "olive", "olio", "oli", "aceto", "aceti",
            "sale", "pepe", "spezia", "spezie", "aroma", "aromi",
            "aglio", "cipolla", "cipolle", "carota", "carote",
            "patata", "patate", "zucchina", "zucchine",
            "melanzana", "melanzane", "peperone", "peperoni",
            "fungo", "funghi", "tartufo", "tartufi",
            "uovo", "uova", "burro", "panna", "yogurt",
            "animale", "animali", "domestico", "domestici",
            "selvatico", "selvatici", "zoo", "giardino", "giardini",
            "cucciolo", "cuccioli", "cucciola", "cucciola",
            "sport", "calcio", "tennis", "pallacanestro", "basket",
            "pallavolo", "nuoto", "ciclismo", "atletica",
            "palestra", "palestre", "allenamento", "allenamenti",
            "partita", "partite", "gara", "gare", "torneo", "tornei",
            "campionato", "campionati", "campionessa", "campionesse",
            "olimpiadi", "mondiali", "europei",
            "giocatore", "giocatrice", "giocatori", "giocatrici",
            "allenatore", "allenatrice", "allenatori",
            "arbitro", "arbitri", "tifoso", "tifosa", "tifosi",
            "stadio", "stadi", "campo", "campi", "piscina", "piscine",
            "montagna", "montagne", "cima", "cime", "vetta", "vette",
            "valle", "valli", "fiume", "fiumi", "torrente", "torrenti",
            "cascata", "cascate", "lago", "laghi", "stagno", "stagni",
            "spiaggia", "spiagge", "sabbia", "sabbie", "scoglio", "scogli",
            "onda", "onde", "marea", "maree", "corrente", "correnti",
            "nuotare", "tuffarsi", "galleggiare", "annegare",
            "pesca", "pesche", "pescare", "pescatore", "pescatori",
            "barca", "barche", "vela", "vele", "remo", "remi",
            "motore", "motori", "timone", "timoni", "ancora", "ancore",
            "relax", "riposo", "divertimento", "divertimenti",
            "gioco", "giochi", "giocattolo", "giocattoli",
            "bambola", "bambole", "puzzle", "costruzioni",
            "carta", "forbici", "colla", "nastro", "adesivo", "adesivi",
            "matita", "matite", "penna", "penne", "pennarello", "pennarelli",
            "gomma", "gomme", "temperino", "temperini", "righello", "righelli",
            "quaderno", "quaderni", "diario", "diari", "zaino", "zaini",
            "astuccio", "astucci", "cartella", "cartelle",
            "lavagna", "lavagne", "gesso", "gessi", "cancellino", "cancellini",
            "cattedra", "cattedre", "banco", "banchi", "aula", "aule",
            "corridoio", "corridoi", "palestra", "palestre", "mensa", "mense",
            "bidello", "bidella", "bidelli", "bidelle",
            "preside", "presidi", "vicepreside", "segreteria", "segreterie",
            "certificato", "certificati", "diploma", "diplomi",
            "attestato", "attestati", "pagella", "pagelle",
            "intervallo", "intervalli", "ricreazione", "ricreazioni",
            "campanella", "campanelle", "suoneria", "suonerie",
            "materia", "materie", "disciplina", "discipline",
            "letteratura", "letterature", "storia", "storie",
            "geografia", "cartina", "cartine", "atlante", "atlanti",
            "cultura", "culture", "tradizione", "tradizioni",
            "usanza", "usanze", "costume", "costumi", "rito", "riti",
            "cerimonia", "cerimonie", "festa", "feste", "ricorrenza", "ricorrenze",
            "compleanno", "compleanni", "anniversario", "anniversari",
            "matrimonio", "matrimoni", "nozze", "sposo", "sposa", "sposi", "spose",
            "battesimo", "battesimi", "comunione", "comunioni", "cresima", "cresime",
            "funerale", "funerali", "lutto", "lutti", "condoglianze",
            "nascita", "nascite", "morte", "morti", "decesso", "decessi",
            "compleanno", "festeggiamento", "festeggiamenti",
            "regalo", "regali", "augurio", "auguri", "sorpresa", "sorprese",
            "invito", "inviti", "partecipazione", "partecipazioni",
            "buffet", "rinfresco", "rinfreschi", "brindisi",
            "salute", "cin", "cin", "cin",
            "emozione", "emozioni", "sentimento", "sentimenti",
            "amore", "amori", "odio", "odii", "rabbia", "rabbie",
            "paura", "paure", "ansia", "ansie", "stress",
            "gioia", "gioie", "felicità", "tristezza", "tristezze",
            "dolore", "dolori", "sofferenza", "sofferenze",
            "piacere", "piaceri", "desiderio", "desideri",
            "speranza", "speranze", "fiducia", "fiducie",
            "coraggio", "coraggi", "pazienza", "impazienza",
            "simpatia", "simpatie", "antipatia", "antipatie",
            "rispetto", "rispetti", "gelosia", "gelosie",
            "invidia", "invide", "orgoglio", "orgogli",
            "vergogna", "vergogne", "imbarazzo", "imbarazzi",
            "sorpresa", "sorprese", "curiosità",
            "interesse", "interessi", "noia", "noie",
            "entusiasmo", "entusiasmi", "passione", "passioni",
            "affetto", "affetti", "tenerezza", "tenerezze",
            "gratitudine", "riconoscenza", "stima", "stime",
            "ammirazione", "ammirazioni", "disprezzo", "disprezzi",
            "sdegno", "sdegni", "indignazione",
            "sollievo", "sollievi", "conforto", "conforti",
            "dispiacere", "dispiaceri", "rimpianto", "rimpianti",
            "rimorso", "rimorsi", "senso", "sensi", "colpa", "colpe",
            "perdono", "perdoni", "scusa", "scuse", "giustificazione", "giustificazioni",
            "verità", "bugia", "bugie", "menzogna", "menzogne",
            "segreto", "segreti", "confidenza", "confidenze",
            "promessa", "promesse", "giuramento", "giuramenti",
            "tradimento", "tradimenti", "fedeltà", "lealtà",
            "onestà", "disonestà", "correttezza", "scorrettezza",
            "educazione", "maleducazione", "gentilezza", "gentilezze",
            "cortesia", "cortesie", "scortesia", "scortesie",
            "buongiorno", "buonasera", "buonanotte", "arrivederci",
            "ciao", "salve", "grazie", "prego", "scusa", "scusi",
            "per favore", "per piacere", "volentieri", "figurati",
            "complimenti", "congratulazioni", "auguri", "condoglianze",
            "benvenuto", "benvenuta", "benvenuti", "benvenute",
            "permesso", "avanti", "prego", "s'accomodi",
            "come", "dove", "quando", "perché", "quanto", "quanti",
            "quale", "quali", "chi", "cosa", "come", "dove",
            "appunto", "insomma", "dunque", "quindi", "cioè",
            "ossia", "ovvero", "oppure", "altrimenti", "invece",
            "comunque", "tuttavia", "eppure", "anzi", "piuttosto",
            "infatti", "inoltre", "peraltro", "tra", "l'altro",
            "specialmente", "soprattutto", "particolarmente",
            "generalmente", "normalmente", "solitamente", "frequentemente",
            "raramente", "occasionalmente", "spesso", "qualche", "volta",
            "improvvisamente", "all'improvviso", "repentinamente",
            "lentamente", "velocemente", "rapidamente", "immediatamente",
            "lentamente", "dolcemente", "gentilmente", "cortesemente",
            "felicemente", "tristemente", "allegramente",
            "naturalmente", "ovviamente", "evidentemente", "certamente",
            "sicuramente", "probabilmente", "possibilmente", "difficilmente",
            "facilmente", "perfettamente", "completamente", "totalmente",
            "assolutamente", "relativamente", "parzialmente",
            "esattamente", "precisamente", "approssimativamente",
            "praticamente", "teoricamente", "praticamente",
            "finalmente", "ultimamente", "recentemente", "precedentemente",
            "attualmente", "nuovamente", "originariamente",
            "personalmente", "individualmente", "collettivamente",
            "direttamente", "indirettamente", "semplicemente", "complessamente",
            "brevemente", "ampiamente", "profondamente", "superficialmente",
        }
        self.words = builtin

    def contains(self, word: str) -> bool:
        return word.lower() in self.words

    def suggest(self, word: str, max_suggestions: int = 5, max_distance: int = 3) -> list:
        """Trova suggerimenti ortografici usando la distanza di Levenshtein."""
        w = word.lower()
        candidates = []
        # Limita la ricerca a parole di lunghezza simile per performance
        wlen = len(w)
        for dict_word in self.words:
            if abs(len(dict_word) - wlen) > max_distance:
                continue
            dist = levenshtein(w, dict_word)
            if dist <= max_distance and dist > 0:
                candidates.append((dict_word, dist))

        # Ordina per distanza, poi alfabeticamente
        candidates.sort(key=lambda x: (x[1], x[0]))
        return [c[0] for c in candidates[:max_suggestions]]


# ---------- Tokenizzazione ----------
def tokenize_text(text: str) -> list:
    """Tokenizza il testo in parole e spazi/punteggiatura, con posizioni."""
    tokens = []
    pos = 0
    # Pattern migliorato: cattura parole (incluse apostrofate), numeri, punteggiatura, spazi
    pattern = re.compile(
        r"([a-zA-ZàèéìòóùÀÈÉÌÒÓÙ']+)|(\d+)|([ \t\r\n]+)|([^\w\s])"
    )
    for m in pattern.finditer(text):
        word = m.group(1)
        number = m.group(2)
        space = m.group(3)
        punct = m.group(4)
        if word:
            tokens.append({
                "text": m.group(0),
                "type": "word",
                "start": m.start(),
                "end": m.end(),
                "word": word,
            })
        elif number:
            tokens.append({
                "text": m.group(0),
                "type": "number",
                "start": m.start(),
                "end": m.end(),
            })
        elif space:
            tokens.append({
                "text": m.group(0),
                "type": "space",
                "start": m.start(),
                "end": m.end(),
            })
        elif punct:
            tokens.append({
                "text": m.group(0),
                "type": "punct",
                "start": m.start(),
                "end": m.end(),
            })
        pos = m.end()
    return tokens


# ---------- Regole grammaticali ----------
GRAMMAR_RULES = [
    # Pattern: parole errate comuni
    {
        "name": "è una → èna (univerbazione errata)",
        "pattern": re.compile(r"\bèna\b", re.IGNORECASE),
        "message": "Errore di univerbazione: scrivi 'è una' separato.",
        "fix": "è una",
    },
    {
        "name": "c'è → cè (accento mancante)",
        "pattern": re.compile(r"\bcè\b", re.IGNORECASE),
        "message": "Manca l'apostrofo: scrivi \"c'è\".",
        "fix": "c'è",
    },
    {
        "name": "po' → po (apostrofo mancante)",
        "pattern": re.compile(r"\bpo\b(?!['’])", re.IGNORECASE),
        "message": "Manca l'apostrofo: scrivi \"po'\" (troncamento di poco).",
        "fix": "po'",
    },
    {
        "name": "un pò → un po' (accento invece di apostrofo)",
        "pattern": re.compile(r"\b(pò)\b", re.IGNORECASE),
        "message": "Usa l'apostrofo, non l'accento: scrivi \"po'\".",
        "fix": "po'",
    },
    {
        "name": "a me mi → a me (pleonasmo)",
        "pattern": re.compile(r"\ba\s+me\s+mi\b", re.IGNORECASE),
        "message": "Pleonasmo: 'a me mi' è ridondante. Scrivi 'a me' o 'mi'.",
        "fix": "a me",
    },
    {
        "name": "ma però → ma (pleonasmo)",
        "pattern": re.compile(r"\bma\s+però\b", re.IGNORECASE),
        "message": "Pleonasmo: 'ma però' è ridondante. Usa solo 'ma' o solo 'però'.",
        "fix": "ma",
    },
    {
        "name": "piuttosto che disgiuntivo",
        "pattern": re.compile(r"\bpiuttosto\s+che\b", re.IGNORECASE),
        "message": "Usa 'o' o 'oppure' per alternative; 'piuttosto che' significa 'anziché'.",
        "fix": "o",
        "requires_context": True,
    },
    {
        "name": "qual'è → qual è (apostrofo errato)",
        "pattern": re.compile(r"\bqual'è\b", re.IGNORECASE),
        "message": "Non si apostrofa: scrivi 'qual è' senza apostrofo (è un troncamento).",
        "fix": "qual è",
    },
    {
        "name": "un'amico → un amico (apostrofo errato)",
        "pattern": re.compile(r"\bun'amico\b", re.IGNORECASE),
        "message": "Si scrive 'un amico' senza apostrofo (amico è maschile).",
        "fix": "un amico",
    },
    {
        "name": "un'uomo → un uomo (apostrofo errato)",
        "pattern": re.compile(r"\bun'uomo\b", re.IGNORECASE),
        "message": "Si scrive 'un uomo' senza apostrofo (uomo è maschile).",
        "fix": "un uomo",
    },
    {
        "name": "d'accordo → daccordo (grafia unita errata)",
        "pattern": re.compile(r"\bdaccordo\b", re.IGNORECASE),
        "message": "Errore di univerbazione: scrivi \"d'accordo\" con apostrofo.",
        "fix": "d'accordo",
    },
    {
        "name": "d'accordo → daccordo varianti",
        "pattern": re.compile(r"\bdaccordo\b", re.IGNORECASE),
        "message": "Errore di univerbazione: scrivi \"d'accordo\" con apostrofo.",
        "fix": "d'accordo",
    },
    {
        "name": "se stesso → sé stesso (accento su sé)",
        "pattern": re.compile(r"\bse\s+stess[oaie]\b", re.IGNORECASE),
        "message": "Il pronome 'sé' vuole l'accento: scrivi 'sé stesso/a/i/e'.",
        "fix": None,  # Richiede sostituzione contestuale
        "requires_context": True,
    },
    {
        "name": "e anziché ed prima di vocale (stile)",
        "pattern": re.compile(r"\be\s+([aeiouàèéìòóùAEIOU])", re.IGNORECASE),
        "message": "Per eufonia, prima di vocale si può usare 'ed' (facoltativo).",
        "fix": None,
        "is_style": True,
    },
]


def check_grammar(text: str) -> list:
    """Applica le regole grammaticali e restituisce gli errori trovati."""
    errors = []
    seen_spans = set()

    for rule in GRAMMAR_RULES:
        for m in rule["pattern"].finditer(text):
            span = (m.start(), m.end())
            # Evita sovrapposizioni
            if any(s[0] < span[1] and span[0] < s[1] for s in seen_spans):
                continue
            seen_spans.add(span)

            fix = rule.get("fix")
            if fix is None and not rule.get("requires_context"):
                continue
            if rule.get("is_style"):
                continue  # Salta regole di stile per ora

            errors.append({
                "start": m.start(),
                "end": m.end(),
                "text": m.group(0),
                "message": rule["message"],
                "suggestions": [fix] if fix else [],
                "type": "grammar",
            })

    return errors


# ---------- Controllore principale ----------
class ItalianChecker:
    """Controllore ortografico e grammaticale per testi italiani."""

    def __init__(self, dict_path: str = None):
        self.dictionary = ItalianDictionary(dict_path)

    def check(self, text: str) -> dict:
        """Analizza il testo e restituisce errori e statistiche."""
        errors = []
        tokens = tokenize_text(text)

        # 1. Controllo ortografico (parola per parola)
        word_errors = {}  # start -> error, per evitare duplicati
        for token in tokens:
            if token["type"] != "word":
                continue
            word = token["word"].lower()
            # Ignora parole molto corte (articoli, preposizioni già nel dizionario)
            if len(word) <= 1:
                continue
            # Ignora parole con apostrofo interno (controllo complesso)
            # Controlla se la parola è nel dizionario
            if not self.dictionary.contains(word):
                # Prova senza apostrofo finale
                clean_word = word.rstrip("'’")
                if clean_word != word and self.dictionary.contains(clean_word):
                    continue
                suggestions = self.dictionary.suggest(word, max_suggestions=5)
                errors.append({
                    "start": token["start"],
                    "end": token["end"],
                    "text": token["text"],
                    "message": f"Possibile errore ortografico: '{token['text']}' non riconosciuto.",
                    "suggestions": suggestions,
                    "type": "spelling",
                })

        # 2. Controllo grammaticale (basato su regole)
        grammar_errors = check_grammar(text)

        # Unisci: errori grammaticali PRIMA, poi ortografici (grammatica ha priorità)
        all_errors = grammar_errors + errors
        all_errors.sort(key=lambda e: e["start"])

        # Rimuovi sovrapposizioni: keep first (grammar errors win)
        filtered = []
        used_spans = set()
        for err in all_errors:
            span = (err["start"], err["end"])
            overlap = False
            for u in used_spans:
                if u[0] < span[1] and span[0] < u[1]:
                    overlap = True
                    break
            if not overlap:
                filtered.append(err)
                used_spans.add(span)
        # Riordina per posizione
        filtered.sort(key=lambda e: e["start"])

        return {
            "errors": filtered,
            "total_words": sum(1 for t in tokens if t["type"] == "word"),
            "error_count": len(filtered),
        }
