from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
import sqlite3
nltk.download('stopwords')
nltk.download('punkt')
import glob  
path = '*.html'
print(path)
files = glob.glob(path) 
countra=0
for name in files:
    #GET HTML CONTENT ELEMENT-less BODY/lowering
    pageContent = open(name, 'r',encoding="utf-8").read()
    pageContent=BeautifulSoup(pageContent).find('body')
    pageContent = pageContent.text.lower()
    conn = sqlite3.connect('inverted-index1.db')
    #Eliminate empty lines
    lines = pageContent.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    pageContent = ""
    for line in non_empty_lines:
        pageContent += line + "\n"
    # print(pageContent)

    #TOKENIZE
    text_tokens = word_tokenize(pageContent)
    # print(text_tokens)
    index=[]
    #FIND INDEX OF ALL UNIQUE WORDS
    inde=""
    position=[]
    repeat=[]
    lila=[]
    i=0
    j=0 
    for coun in text_tokens:
        for coun2 in text_tokens:
            if(coun==coun2):
                inde=inde + "," + f'{j}'
            j=j+1
        position=position+[inde]
        inde=""
        j=0
    lila = list(dict.fromkeys(position))
    position=lila


    #ELIMINATE STOPWORDS
    stpwrd=nltk.corpus.stopwords.words('english')
    new_stopwords=["ter","nov","novo", "nova","zato","še", "zaradi", "a", "ali", "april", "avgust", "b", "bi", "bil", "bila", "bile", "bili", "bilo", "biti",
            "blizu", "bo", "bodo", "bojo", "bolj", "bom", "bomo", "boste", "bova", "boš", "brez", "c", "cel", "cela",
            "celi", "celo", "d", "da", "daleč", "dan", "danes", "datum", "december", "deset", "deseta", "deseti", "deseto",
            "devet", "deveta", "deveti", "deveto", "do", "dober", "dobra", "dobri", "dobro", "dokler", "dol", "dolg",
            "dolga", "dolgi", "dovolj", "drug", "druga", "drugi", "drugo", "dva", "dve", "e", "eden", "en", "ena", "ene",
            "eni", "enkrat", "eno", "etc.", "f", "februar", "g", "g.", "ga", "ga.", "gor", "gospa", "gospod", "h", "halo",
            "i", "idr.", "ii", "iii", "in", "iv", "ix", "iz", "j", "januar", "jaz", "je", "ji", "jih", "jim", "jo",
            "julij", "junij", "jutri", "k", "kadarkoli", "kaj", "kajti", "kako", "kakor", "kamor", "kamorkoli", "kar",
            "karkoli", "katerikoli", "kdaj", "kdo", "kdorkoli", "ker", "ki", "kje", "kjer", "kjerkoli", "ko", "koder",
            "koderkoli", "koga", "komu", "kot", "kratek", "kratka", "kratke", "kratki", "l", "lahka", "lahke", "lahki",
            "lahko", "le", "lep", "lepa", "lepe", "lepi", "lepo", "leto", "m", "maj", "majhen", "majhna", "majhni",
            "malce", "malo", "manj", "marec", "me", "med", "medtem", "mene", "mesec", "mi", "midva", "midve", "mnogo",
            "moj", "moja", "moje", "mora", "morajo", "moram", "moramo", "morate", "moraš", "morem", "mu", "n", "na", "nad",
            "naj", "najina", "najino", "najmanj", "naju", "največ", "nam", "narobe", "nas", "nato", "nazaj", "naš", "naša",
            "naše", "ne", "nedavno", "nedelja", "nek", "neka", "nekaj", "nekatere", "nekateri", "nekatero", "nekdo",
            "neke", "nekega", "neki", "nekje", "neko", "nekoga", "nekoč", "ni", "nikamor", "nikdar", "nikjer", "nikoli",
            "nič", "nje", "njega", "njegov", "njegova", "njegovo", "njej", "njemu", "njen", "njena", "njeno", "nji",
            "njih", "njihov", "njihova", "njihovo", "njiju", "njim", "njo", "njun", "njuna", "njuno", "no", "nocoj",
            "november", "npr.", "o", "ob", "oba", "obe", "oboje", "od", "odprt", "odprta", "odprti", "okoli", "oktober",
            "on", "onadva", "one", "oni", "onidve", "osem", "osma", "osmi", "osmo", "oz.", "p", "pa", "pet", "peta",
            "petek", "peti", "peto", "po", "pod", "pogosto", "poleg", "poln", "polna", "polni", "polno", "ponavadi",
            "ponedeljek", "ponovno", "potem", "povsod", "pozdravljen", "pozdravljeni", "prav", "prava", "prave", "pravi",
            "pravo", "prazen", "prazna", "prazno", "prbl.", "precej", "pred", "prej", "preko", "pri", "pribl.",
            "približno", "primer", "pripravljen", "pripravljena", "pripravljeni", "proti", "prva", "prvi", "prvo", "r",
            "ravno", "redko", "res", "reč", "s", "saj", "sam", "sama", "same", "sami", "samo", "se", "sebe", "sebi",
            "sedaj", "sedem", "sedma", "sedmi", "sedmo", "sem", "september", "seveda", "si", "sicer", "skoraj", "skozi",
            "slab", "smo", "so", "sobota", "spet", "sreda", "srednja", "srednji", "sta", "ste", "stran", "stvar", "sva",
            "t", "ta", "tak", "taka", "take", "taki", "tako", "takoj", "tam", "te", "tebe", "tebi", "tega", "težak",
            "težka", "težki", "težko", "ti", "tista", "tiste", "tisti", "tisto", "tj.", "tja", "to", "toda", "torek",
            "tretja", "tretje", "tretji", "tri", "tu", "tudi", "tukaj", "tvoj", "tvoja", "tvoje", "u", "v", "vaju", "vam",
            "vas", "vaš", "vaša", "vaše", "ve", "vedno", "velik", "velika", "veliki", "veliko", "vendar", "ves", "več",
            "vi", "vidva", "vii", "viii", "visok", "visoka", "visoke", "visoki", "vsa", "vsaj", "vsak", "vsaka", "vsakdo",
            "vsake", "vsaki", "vsakomur", "vse", "vsega", "vsi", "vso", "včasih", "včeraj", "x", "z", "za", "zadaj",
            "zadnji", "zakaj", "zaprta", "zaprti", "zaprto", "zdaj", "zelo", "zunaj", "č", "če", "često", "četrta",
            "četrtek", "četrti", "četrto", "čez", "čigav", "š", "šest", "šesta", "šesti", "šesto", "štiri", "ž", "že",
            "svoj", "jesti", "imeti","\u0161e", "iti", "kak", "www", "km", "eur", "pač", "del", "kljub", "šele", "prek",
            "preko", "znova", "morda","kateri","katero","katera", "ampak", "lahek", "lahka", "lahko", "morati", "torej", ".", 
             ",","?","!","(",")","/","\"","{","}",":",";","'","`","_", "<", ">","...","---","..","--","''"]
    stpwrd.extend(new_stopwords)
    tokens_without_sw = [words for words in text_tokens if not words in stpwrd]
    temp_list = []
    for i in tokens_without_sw:
        if i not in temp_list:
            temp_list.append(i)
    tokens_without_sw = temp_list
    # print(tokens_without_sw)

    # print(len(tokens_without_sw))

    #ON WHAT POSITION STOPWORDS
    indeksar=[]
    for crc in stpwrd:
        for tex in text_tokens:
            if(crc==tex):
                indeksar=indeksar+ [text_tokens.index(tex)]
                break
    indeksar = list(dict.fromkeys(indeksar))
    # indeksar=sorted(indeksar)
    # print(indeksar)
    #WHERE IS IT FIRST APPEARING
    intstring=[]
    stringovi={}
    truplo=position
    j=0
    for i in range(len(position)):  
        stringovi=position[i]
        stringovi=stringovi[1:]
        # print(stringovi)
        stringovi=stringovi.split(',')
        stringovi=stringovi[0]
        intstring.append(int(stringovi))
        stringovi={}
    # print(intstring)
    #UPDATE POSITIONS 
    j=0
    for fgf in indeksar:
        for i in intstring:
            if(i==fgf):
                truplo.pop(j)
                intstring.pop(j)
                continue  
            else:
                j=j+1     
        j=0
    position=truplo
    # print(len(position))

    #CALCILATE FREQUENCY
    stringovi={}
    freq=[]
    j=0
    x=0
    #FREQUENCY
    for i in range(len(position)):  
        stringovi=position[i]
        stringovi=stringovi[1:]
        x=([int(s) for s in stringovi.split(',')])
        freq.append(len(x)) 
    # print(freq)
    # print(len(freq))
    
    c = conn.cursor()
    if countra==0:
        c.execute('''
            CREATE TABLE IndexWord (
                word TEXT PRIMARY KEY
            );
        ''')

        c.execute('''
            CREATE TABLE Posting (
                word TEXT NOT NULL,
                documentName TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                indexes TEXT NOT NULL,
                PRIMARY KEY(word, documentName),
                FOREIGN KEY (word) REFERENCES IndexWord(word)
            );
        ''')

    countra=1

    # # Save (commit) the changes
    # conn.commit()
    g=[]
    #INSERT INSIDE ONLY IF DOES NOT EXIST
    for item in tokens_without_sw:
        c.execute("SELECT word FROM IndexWord WHERE word= ?", (item,) )
        g=c.fetchone()
        if g is None:
            c.execute("INSERT INTO IndexWord(word) VALUES(?)", (item,))
    conn.commit()
    # Save (commit) the changes
    # conn.close()
    x=[]
    y=[]
    docName=[]
    shh=[]
    for krak in range(len(freq)):
        docName.append(name)
    # print(len(docName))

    # x=list(zip(tokens_without_sw,docName,freq,position))
    #INSERT FOR EACH PAGE WORD ENTRY
    
    for i in range(len(freq)):
            c.execute("INSERT INTO Posting(word,documentName,frequency,indexes) VALUES(?, ?, ?, ?)", (tokens_without_sw[i],docName[i],freq[i],position[i][1:],))
    conn.commit()
    # Save (commit) the changes
    conn.close()

