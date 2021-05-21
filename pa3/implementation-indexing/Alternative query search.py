import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
import sqlite3
from bs4 import BeautifulSoup
import glob 
nltk.download('stopwords')
nltk.download('punkt')

querry = input("Enter querry:")
querry=querry.lower()
# print(querry)
conn = sqlite3.connect('inverted-index1.db')
querry_token = word_tokenize(querry)
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
tokens_without_sw = [words for words in querry_token if not words in stpwrd]
temp_list = []
for i in tokens_without_sw:
    if i not in temp_list:
        temp_list.append(i)
tokens_without_sw = temp_list
# print(tokens_without_sw)
lipa=[]
# print(lipa)
print(f"\tFrequency:\t\tDocument:\t\t\tSnippet:\n")
print(f"\t------------\t\t---------------------\t\t---------------------------------------\n")
for token in tokens_without_sw:
    cursor = conn.execute('''
        SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
        FROM Posting p
        WHERE
            p.word  =  ?
        GROUP BY p.documentName
        ORDER BY freq DESC;
    ''', (token,))

    for row in cursor:
        
        namea=row[0]
        pageContent = open(namea, 'r',encoding="utf-8").read()
        pageContent=BeautifulSoup(pageContent).find('body')
        pageContent = pageContent.text.lower()
        lines = pageContent.split("\n")
        non_empty_lines = [line for line in lines if line.strip() != ""]
        pageContent = ""
        for line in non_empty_lines:
            pageContent += line + "\n"
        text_tokens = word_tokenize(pageContent)
        inde=""
        position=[]
        repeat=[]
        lila=[]
        i=0
        j=0 
        x=0
        for coun in text_tokens:
            for coun2 in text_tokens:
                if(coun==coun2):
                    inde=inde + "," + f'{j}'
                j=j+1
            position=position+[inde]
            inde=""
            j=0
        count=0
        lila = list(dict.fromkeys(position))
        position=lila
        for toki in text_tokens:
            if token==toki:
                x=text_tokens.index(toki)
                if count ==0:
                    if x==0:
                        print(f"\t{row[1]}\t\t\t{row[0]}\t\t\n"+text_tokens[x]+ " "+text_tokens[x+1]+ " "+text_tokens[x+2]+"...")
                        count=count+1
                    if x==1:
                        print(f"\t{row[1]}\t\t\t{row[0]}\t\t\n"+"..." + text_tokens[x-1]+" " +text_tokens[x]+ " "+text_tokens[x+1]+ " "+text_tokens[x+2]+text_tokens[x+3]+"...")
                        count=count+1
                    if x==2:
                        print(f"\t{row[1]}\t\t\t{row[0]}\t\t\n"+"..." + text_tokens[x-2]+" " + text_tokens[x-1]+" " +text_tokens[x]+ " "+text_tokens[x+1]+ " "+text_tokens[x+2]+text_tokens[x+3]+"...")
                        count=count+1
                    if x>=3:
                        print(f"\t{row[1]}\t\t\t{row[0]}\t\t\n"+"..."+ " "+ text_tokens[x-3]+" " + text_tokens[x-2]+" " + text_tokens[x-1]+" " + text_tokens[x]+" " + text_tokens[x+1]+" " + text_tokens[x+2]+" " + text_tokens[x+3]+"...")
                        count=count+1
        count=0
        



                    


























