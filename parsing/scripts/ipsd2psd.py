import sys
import re

# Define RegEx patterns for Icelandic characters and sets of definite nouns
allchars = 'a-zA-ZþæðöÞÆÐÖáéýúíóÁÉÝÚÍÓ\.$'
enCase = {'n':'N','o':'A','þ':'D','e':'G'}
lemmas={}
# Faroese modals
modal = "skula|skulu|munna|munu|mega|vilja|geta"

def rep( before, after ):
	global currentText 
	currentText = re.sub( before, after, currentText )

def treebank_tag( icenlp_tag ):

    # c-tags
    if icenlp_tag == "c":
        return "C"
    if icenlp_tag == "ct":
        return "CT"

    # foreign words
    if icenlp_tag == "e":
        return "FW"

    # injp
    if icenlp_tag == "au":
        return "INTJ"

    # adverbs
    if icenlp_tag == "aa":
        return "ADV"
    if icenlp_tag == "aam":
        return "ADVR"
    if icenlp_tag == "aae":
        return "ADVS"

    # prepositions
    if re.match( "a[oþe]", icenlp_tag ):
        return "P"

    # infinitival marker
    if icenlp_tag == "cn":
        return "TO"

    # numbers
    if re.match( "t[anoþe]", icenlp_tag):
        case = re.search("t([anoþe])",icenlp_tag).group(1)
        if case == "a":
            case = "n"
        return "NUM-"+enCase[case]

    if re.match( "t[a-z]{3}[noþe]", icenlp_tag):
        case = re.search("t[a-z]{3}([noþe])",icenlp_tag).group(1)
        return "NUM-"+enCase[case]

    # nouns
    if re.match("n[a-zþ\-]{3,5}", icenlp_tag):
        nounTag = "N"
        if re.match("n[a-zþ\-]{5}", icenlp_tag):
            nounTag = nounTag + "PR"
        if re.match("n[a-z]f[a-zþ\-]{1,3}", icenlp_tag):
            nounTag = nounTag + "S"
        nounTag = nounTag+"-"+enCase[icenlp_tag[3]]
        return nounTag

    # determiners
    if icenlp_tag.startswith("g"):
        detTag = "D"
        detTag = detTag+"-"+enCase[icenlp_tag[3]]
        return detTag

    if icenlp_tag.startswith("f"):
        proTag = "PRO"
        proTag = proTag +"-"+enCase[icenlp_tag[4]]
        return proTag

    # verbs
    if icenlp_tag == "slg":
        return "VAG"
    if icenlp_tag.startswith("sb"):
        return "VBI"
    if re.match("sn[gm]", icenlp_tag):
        return "VB"
    if re.match("ss[gm]", icenlp_tag):
        return "VBN"
    if re.match("sþ[a-zþ]{4}",icenlp_tag):
        return "VAN"
    if re.match("sf[a-z1-3]{3}n",icenlp_tag):
        return "VBPI"
    if re.match("sf[a-z1-3]{3}þ",icenlp_tag):
        return "VBDI"
    if re.match("sv[a-z1-3]{3}n",icenlp_tag):
        return "VBPS"
    if re.match("sv[a-z1-3]{3}þ",icenlp_tag):
        return "VBDS"

    # adjectives
    if re.match("l[a-zþ]{5}",icenlp_tag):
        adjtag="ADJ"
        if re.match("l[a-zþ]{4}m",icenlp_tag):
            adjtag=adjtag+"R"
        if re.match("l[a-zþ]{4}e",icenlp_tag):
            adjtag=adjtag+"S"
        adjtag=adjtag+"-"+enCase[icenlp_tag[3]]
        return adjtag
    
    return icenlp_tag

def get_lemma(word,tag):
	if word+"-"+tag in lemmas:
		return lemmas[word+"-"+tag]
	else:
		return word

def convert_tag( match ):
        tagPattern="(["+allchars+"\_\-0-9]+) (["+allchars+"\_\-0-9]+)"
        theTag = re.search(tagPattern,match.group()).group(1)
        theWord = re.search(tagPattern,match.group()).group(2)
        theLemma = get_lemma(theWord,theTag)

        # check for 2n person clitic
        if re.match("s[a-z]{2}2[a-zþ]{2}",theTag) and re.match("['"+allchars+"']+(ððu|ðdu|ðtu)$",theWord):
            verbstem = re.search("(['"+allchars+"']+)(ððu|ðdu|ðtu)$",theWord).group(1) #does not apply to Faroese, probably
            clitic = re.search("(['"+allchars+"']+)(ðu|du|tu)$",theWord).group(2)
            # print(theWord + " "+theTag)
            return "("+treebank_tag(theTag)+" "+verbstem+"$-"+theLemma+") (NP-SBJ (PRO-N $"+clitic+"-þú))"
            
        # check for suffixed determiner
        determiner=None
        detmatch1="(["+allchars+"]+)(an|inn|inum|ins|ini|inir|ina|inna|in|inni|innar|inar|ið|inu)$"
        detmatch2="(["+allchars+"]+)(num|ns|nir|nna|nn|nni|n{1,2}ar|ð|nu)$"
        detmatch3="(["+allchars+"]+)(n|na)$"
        if re.match("n[a-zþ]{3}g[a-zþ]*",theTag) and (re.match(detmatch1,theWord) or re.match(detmatch2,theWord)):
            # there is a determiner
            currentMatch = None
            if re.match(detmatch1,theWord):
                currentMatch = detmatch1
            elif re.match(detmatch2,theWord):
                currentMatch = detmatch2
            elif re.match(detmatch3,theWord):
                currentMatch = detmatch3

#            print(theWord + " "+theTag)
            determiner = re.search(currentMatch,theWord).group(2)
            theWord = re.search(currentMatch,theWord).group(1)

        theTag = treebank_tag(theTag)
#        if( theWord == "." ):
#               return "(. .)"
        if determiner == None:
            output = "("+theTag+" "+theWord+"-"+theLemma+")"
        else:
            chunks = theTag.split("-")
            output = "("+theTag+" "+theWord+"$-"+theLemma+") (D-"+chunks[1]+" $"+determiner+"-hinn)"
        return output

# Open input file for reading

def remove_extra_ipsd_stuff():
    # Remove extra stuff
    rep("[\<\>]","")
    rep("MWE\_","")

    rep("\{\*TIMEX ","")
    rep("\*TIMEX\}","")
 #   rep("\{\*COMP ","")
 #   rep("\*COMP\}","")
    rep("\[NPs","[NP")
    rep("NPs\]","NP]")
    rep("\[APs","[AP")
    rep("APs\]","AP]")
    rep("\[VPs","[VP")
    rep("VPs\]","VP]")


def load_lemmas():
    # Read lemmas from file
    lemmaFile=open(sys.argv[1]+".lemmatized",'r')
    lines=lemmaFile.readlines()
    for line in lines:
            chunks=line.split(" ")
            if len(chunks)>2:
                    theLemma = chunks[2].strip().lower()
                    theLemma = theLemma.replace("(","")
                    theLemma = theLemma.replace(")","")
                    lemmas[chunks[0]+"-"+chunks[1]]=theLemma


def convert_iceparser_functions():
    # Open syntactic function bracket
    rep("\{\*OBJAP* \[NP","(NP-OB1")
    rep("\{\*OBJNOM* \[NP","(NP-OB1")
    rep("\{\*SUBJ* \[NP","(NP-SBJ")
    rep("\{\*OBJ* \[NP","(NP-OB1")
    rep("\{\*IOBJ* \[NP","(NP-OB2")
    rep("\{\*COMP* \[NP","(NP-PRD")

    # Close syntactic function bracket
    rep("\*(SUBJ|OBJ|OBJAP|IOBJ|COMP|OBJNOM)*\}","")

    # Throw away remaining opening brackets
    rep("\{\*(SUBJ|OBJ|IOBJ|COMP)","")

    # NP-POS
    rep("\{\*QUAL \[NP","(NP-POS")
    rep(" NP\] \*QUAL\}",")")

def convert_brackets_to_pars():
    # Convert brackets to parenthteses
    rep("\[","(")
    rep(" [A-Za-z_]+\]",")")

def parenthesize_punctuation():
    rep("\. \.","(. .)")
    rep("\, \,","(, ,-,)")
    rep("\: \:","(, :-:)")
    rep("\; \;","(. ;-;)")
    rep("\! \!","(. !-!)")
    rep("\? \?","(. ?-?)")
    rep("\- \-","(, -)")
    rep("\" \"","(\" \")")

def convert_phrase_labels():
    # Make Phrase labels uppercase
    rep("\(AdvP","(ADVP")
    rep("\(InjP","(INTJP")
    rep("\(VPi","(IP-INF")
    rep("\(VPp","(VP")
    rep("\(VPb","(VP")
    rep("\(VPg","(VP")
    rep("\(VPs","(VP")
    # Rename some phrase labels
    rep("\(AP","(ADJP")
    
def make_tag_word_pars():
    # Make tag+word parentheses
    global currentText
    currentText = re.sub("\((["+allchars+"\-0-9]+) (["+allchars+"0-9\_\-—]+) (["+allchars+"0-9\_\-]+)","(\\1 (\\3 \\2)",currentText)
    while re.search("\)[ ]{1,2}(["+allchars+"0-9\_\-—]+) (["+allchars+"0-9\_\-]+)", currentText):
            currentText = re.sub("\)[ ]{1,2}(["+allchars+"0-9\_\-—]+) (["+allchars+"0-9\_\-]+)",") (\\2 \\1)",currentText)

def add_ip_mat():
    global currentText
    currentText = re.sub("\)[ ]{0,1}\n\n\(",")))\n\n((IP-MAT (",currentText)
    currentText = "((IP-MAT " + currentText.strip() + "))"

def split_determiners():
    global currentText
    nounMatch = '\(n([a-z]{3})g[a-z]* (['+allchars+']+)(inn|inum|ins|inir|ina|ini|inna|in|inni|innar|inar|ið|inu)-(['+allchars+']+)\)'
    nounMatch2 = '\(n([a-z]{3})g[a-z]* (['+allchars+']+)(num|ns|nir|n{1,2}a|n{1,2}|nni|n{1,2}ar|ð|nu)-(['+allchars+']+)\)'

def convert_tags_to_icepahc():
    # Convert tags from icenlp format to icepahc format
    global currentText
    tagMatch = re.compile("\((["+allchars+"\_\-0-9]+) (["+allchars+"\_\-0-9]+)\)")
    currentText = tagMatch.sub( convert_tag, currentText )

def replace_special_verb_tags():
    global currentText
    # infinitives
    currentText = re.sub("\(VB (["+allchars+"]+)\-vera\)","(BE \\1-vera)", currentText)
    currentText = re.sub("\(VB (["+allchars+"]+)\-(gera|gjöra)\)","(DO \\1-gera)", currentText)
    currentText = re.sub("\(VB (["+allchars+"]+)\-verða\)","(RD \\1-verða)", currentText)
    currentText = re.sub("\(VB (["+allchars+"]+)\-hafa\)","(HV \\1-hafa)", currentText)    
    currentText = re.sub("\(VB (["+allchars+"]+)\-("+modal+")\)","(MD \\1-\\2)", currentText)

    # present participle
    currentText = re.sub("\(VAG (["+allchars+"]+)\-vera\)","(BAG \\1-vera)", currentText)
    currentText = re.sub("\(VAG (["+allchars+"]+)\-(gera|gjöra)\)","(DAG \\1-gera)", currentText)
    currentText = re.sub("\(VAG (["+allchars+"]+)\-verða\)","(RAG \\1-verða)", currentText)
    currentText = re.sub("\(VAG (["+allchars+"]+)\-hafa\)","(HAG \\1-hafa)", currentText)    
    currentText = re.sub("\(VAG (["+allchars+"]+)\-hava\)","(HAG \\1-hava)", currentText)    

    # passive participle
    currentText = re.sub("\(VAN (["+allchars+"]+)\-hava\)","(HAN \\1-hava)", currentText)
    currentText = re.sub("\(VAN (["+allchars+"]+)\-hafa\)","(HAN \\1-hafa)", currentText)
    currentText = re.sub("\(VAN (["+allchars+"]+)\-verða\)","(RDN \\1-verða)", currentText)
    currentText = re.sub("\(VAN (["+allchars+"]+)\-(gera|gjöra)\)","(DAN \\1-gera)", currentText)
    currentText = re.sub("\(VAN (["+allchars+"]+)\-(koma)\)","(VBN \\1-koma)", currentText)

    # perfect participle
    currentText = re.sub("\(VBN (["+allchars+"]+)\-vera\)","(BEN \\1-vera)", currentText)
    currentText = re.sub("\(VBN (["+allchars+"]+)\-verða\)","(RDN \\1-verða)", currentText)
    currentText = re.sub("\(VBN (["+allchars+"]+)\-(gera|gjöra)\)","(DON \\1-gera)", currentText)
    currentText = re.sub("\(VBN (["+allchars+"]+)\-hafa\)","(HVN \\1-hafa)", currentText)
    currentText = re.sub("\(VBN (["+allchars+"]+)\-hava\)","(HVN \\1-hava)", currentText)

    # imperative
    currentText = re.sub("\(VBI (["+allchars+"]+)\-vera\)","(BEI \\1-vera)", currentText)
    currentText = re.sub("\(VBI (["+allchars+"]+)\-(gera|gjöra)\)","(DOI \\1-gera)", currentText)
    currentText = re.sub("\(VBI (["+allchars+"]+)\-verða\)","(RDI \\1-verða)", currentText)
    currentText = re.sub("\(VBI (["+allchars+"]+)\-hafa\)","(HVI \\1-hafa)", currentText)
    currentText = re.sub("\(VBI (["+allchars+"]+)\-hava\)","(HVI \\1-hava)", currentText)
    currentText = re.sub("\(VBI (["+allchars+"]+)\-("+modal+")\)","(MDI \\1-\\2)", currentText)

    # present and past (including subjunctive)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-vera\)","(BE\\1\\2 \\3-vera)", currentText)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-(gera|gjöra)\)","(DO\\1\\2 \\3-gera)", currentText)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-hafa\)","(HV\\1\\2 \\3-hafa)", currentText)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-hava\)","(HV\\1\\2 \\3-hava)", currentText)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-verða\)","(RD\\1\\2 \\3-verða)", currentText)
    currentText = re.sub("\(VB([PD])([IS]) (["+allchars+"]+)\-("+modal+")\)","(MD\\1\\2 \\3-\\4)", currentText)
    
    #reps["\(VBD-([IS])[A-Z123]{4} (["+allchars+"]+)-vera\)"]="(BED\\1 \\2-vera)"  # BED 	BE, past (including past subjunctive)
    #reps["\(VBP-([IS])[A-Z123]{4} (["+allchars+"]+)-vera\)"]="(BEP\\1 \\2-vera)"  # BEI 	BE, present (including present subjunctive)


# This renames stuff and builds/removes some pieces of structure
def final_replacements():
    global currentText

    # ONE 	the word ONE (except as focus particle)
    currentText = re.sub("\((NUM|ADJ|PRO)-([NADG] ["+allchars+"]+-einn)\)","(ONE-\\2)",currentText)

    # samur
    currentText = re.sub("\((PRO)-([NADG] ["+allchars+"]+-samur)\)","(ADJ-\\2)",currentText)

    # hinn
    currentText = re.sub("\(PRO-(N) ([Hh]inn)-hinn\)","(D-\\1 \\2-hinn)",currentText)

    # NEGATION
#    currentText = re.sub("\(ADVP \(ADV ([Ee]kki|[Ee]igi|[Ee]i)-(ekki|eigi|ei)\)\)","(NEG \\1-\\2)",currentText)
    # CONJUNCTIONS
    currentText = re.sub("\(CP \(C ([Oo]g|[Ee]n|[Ee]ða|[Ee]ður|[Ee]llegar|[Hh]eldur|[Ee]nda)-([Oo]g|[Ee]n|[Ee]ða|[Ee]ður|[Ee]llegar|[Hh]eldur|[Ee]nda)\)\)","(CONJ \\1-\\2)",currentText)
    rep("\(SCP \(C bæði\-bæði\)\)","(CONJ bæði-bæði)")
    rep("\(CP \(C né-né\)\)","(CONJ né-né)")
    # Quantifiers
    rep("\(PRO-([A-Z]) (["+allchars+"]+)-(allur|báðir|nokkur|enginn|sumur|fáeinir|fár|einhver|neinn|ýmis)\)","(Q-\\1 \\2-\\3)")
    # Demonstratives
    rep("\(PRO-([A-Z]) (["+allchars+"]+)-(hinn)\)","(D-\\1 \\2-\\3)")

    # WQ
    rep("\(PRO-([A-Z]) (["+allchars+"]+)-(hvor)\)","(Q-\\1 \\2-\\3)")


    # Make sjálfur -PRN
    # (NP-SBJ (PRO-N sjálfur-sjálfur))
    rep("\(NP-SBJ \(PRO-([A-Z]) (["+allchars+"]+)-(sjálfur)\)\)","(NP-PRN (PRO-\\1 \\2-\\3))")
    rep("\(PRO-([A-Z]) (["+allchars+"]+)-(sjálfur)\)","(NP-PRN (PRO-\\1 \\2-\\3))")
    rep("\(NP-PRN \(NP-PRN \(PRO-([A-Z]) (["+allchars+"]+)-(sjálfur)\)\)\)","(NP-PRN (PRO-\\1 \\2-\\3))")

    # Focus particle
    rep("\(ADVP \(ADV aðeins-aðeins\)\)","(FP aðeins-aðeins)")
    rep("\(ADV aðeins-aðeins\)","(FP aðeins-aðeins)")

    # ALSO
    rep("\(ADVP \(ADV líka-líka\)\)","(ALSO líka-líka)")
    rep("\(ADVP \(ADV einnig-einnig\)\)","(ALSO einnig-einnig)")

    # heldur
    rep("\(CONJ heldur-heldur\)","(ADVP (ADVR heldur-heldur))")

    # negation, ekki and eigi
    rep("\(ADV ekki-ekki\)","(NEG ekki-ekki)")
    rep("\(NEG eigi-eigi\)","(NEG eigi-ekki)")
    rep("\(ADV eigi-eigi\)","(NEG eigi-ekki)")
    rep("\(ADV Eigi-eigi\)","(NEG Eigi-ekki)")
    rep("\(ADV Ekki-ekki\)","(NEG Ekki-ekki)")
    rep("\(NEG Eigi-eigi\)","(NEG Eigi-ekki)")

    # relative clauses
    rep("\(SCP \(CT ([Ss])em-sem\)\)","(CP-REL (WNP 0) (C \\1em-sem))")
    rep("\(SCP \(CT er-er\)\)","(CP-REL (WNP 0) (C er-er))")

    # margur and mikill
    rep("\(ADJ-([NADG]) ([Mm][aö]rg[a-z]+)-margur\)","(Q-\\1 \\2-margur)")
    rep("\(ADJR-([NADG]) ([Ff]leir[a-z]+)-margur\)","(QR-\\1 \\2-margur)")
    rep("\(ADJS-([NADG]) ([Ff]lest[a-z]+)-(margur|fles[a-z]+)\)","(QS-\\1 \\2-margur)")
    rep("\(ADJ-([NADG]) ([Mm]iki[a-zð]+)-mikill\)","(Q-\\1 \\2-mikill)")
    rep("\(ADJR-([NADG]) ([Mm]eir[a-z]+)-mikill\)","(QR-\\1 \\2-mikill)")
    rep("\(ADVR ([Mm]eir[a-z]*)-meira\)","(QR-N \\1-mikill)")
    rep("\(ADJS-([NADG]) ([Mm]est[a-z]+)-mikill\)","(QS-\\1 \\2-mikill)")

    # einhver
    rep("\(Q-([NADG]) (einhve[a-z]+)-einhver\)","(ONE+Q-\\1 \\2-einhver)")

    # demonstratives
    rep("\(PRO-([NADG]) (["+allchars+"]+-sá)\)","(D-\\1 \\2)")
    rep("\(PRO-([NADG]) (["+allchars+"]+-þessi)\)","(D-\\1 \\2)")

    # OTHER
    rep("\(PRO-([NADG] ["+allchars+"]+-annar)\)","(OTHER-\\1)")

    # eins og
    rep("\(ADV eins-eins\)","(ADVR eins-eins)")
    rep("\(CP \(ADVR eins-eins\) \(C og-og\)\)","(ADVP (ADVR eins) (PP (P og)))")

    # til (þess) að
    #(CP (P til-til) (TO að-að))
    #(CP (P til-til) (PRO-G þess-það) (TO að-að))
    rep("\(CP \(P til-til\) \(TO að-að\)\)","(PP (P til-til) (TO að-að))")
    rep("\(CP \(P til-til\) \(PRO-G þess-það\)","(PP (P til-til) (PRO-G þess-það)")
    rep("\(PP \(P til-til\) \(PRO-G þess-það\) \(TO að-að\)\)","(PP (P til-til) (NP (PRO-G þess-það)) (IP-INF-PRP (C að-að)))")
    #  (PP (P til-til) (PRO-G þess-það) (TO að-að))

    # (af) því að
    rep("\(CP \(ADV því-því\) \(C að-að\)\)","(PP (P 0) (NP (PRO-D því-það) (CP-THT-PRN (C að-að))))")
    rep("\(CP \(PRO-D því-það\) \(C að-að\)\)","(PP (P 0) (NP (PRO-D því-það) (CP-THT-PRN (C að-að))))")
    rep("\(CP \(P af-af\) \(PRO-D því-það\) \(C að-að\)\)","(PP (P af-af) (NP (PRO-D því-það) (CP-THT-PRN (C að-að))))")
       #(CP (P af-af) (PRO-D því-það) (C að-að))

    # þótt að
    rep("\(CP \(ADV þó-þó\) \(C að-að\)\)","(PP (P þó-þó) (CP-ADV (C að-að)))")
    rep("\(CP \(ADV þótt-þótt\) \(C að-að\)\)","(PP (P þótt-þótt) (CP-ADV (C að-að)))")

    # svo að
    rep("\(CP \(ADV svo-svo\) \(C að-að\)\)","(PP (P svo-svo) (CP-ADV (C að-að)))")
    rep("\(CP \(ADV þar-þar\) \(C sem-sem\)\)","(CP-REL (ADV þar-þar) (C sem-sem))")

    # svo sem 
    rep("\(ADV svo-svo\) \(ADV sem-sem\)","(ADV svo-svo) (C sem-sem)")

    # more
    rep("\(SCP ","(CP-ADV ")
    rep("\(CP-ADV \(C að-að\)\)","(CP-THT (C að-að))")

    # fix þótt að
    rep("\(PP \(P þó-þó\) \(CP-THT \(C að-að\)\)\)","(PP (P þó-þó) (CP-ADV (C að-að)))")
    rep("\(PP \(P Þó-þó\) \(CP-THT \(C að-að\)\)\)","(PP (P Þó-þó) (CP-ADV (C að-að)))")
    rep("\(CP-ADV \(C þótt-þótt\)\)\n\(CP-THT \(C að-að\)\)","(PP (P þótt-þótt) (CP-ADV (C að-að)))")
    rep("\(CP-ADV \(C Þótt-þótt\)\)\n\(CP-THT \(C að-að\)\)","(PP (P Þótt-þótt) (CP-ADV (C að-að)))")

    # ef að
    rep("\(CP-ADV \(C ef-ef\)\)\n\(CP-THT \(C að-að\)\)","(PP (P ef-ef) (CP-ADV (C að-að)))")
    rep("\(CP-ADV \(C Ef-ef\)\)\n\(CP-THT \(C að-að\)\)","(PP (P Ef-ef) (CP-ADV (C að-að)))")

    # ADVP-TMP
    currentText = re.sub("\(ADVP \(ADV ([Þþ]á|[Nn]ú|[Áá]ður|[Ææ]tíð|[Aa]ldrei|[Aa]ldregi|[Áá]rla|[Áá]vallt|[Bb]rátt|[Ss]nemma|[Ll]oks|[Ll]oksins|[Oo]ft|[Oo]fvalt|[Ss]eint|[Ss]jaldan|[Ss]nemma|[Þþ]egar|[Ss]íðan)-(["+allchars+"]+)\)\)","(ADVP-TMP (ADV \\1-\\2))",currentText)

    # ADVP-LOC
    currentText = re.sub("\(ADVP \(ADV ([Þþ]ar|[Hh]ér|[Þþ]arna|[Hh]érna|[Hh]eima|[Uu]ppi|[Nn]iðri|[Vv]íða|[Óó]víða|[Aa]llvíða|[Úú]ti|[Ii]nni)-(["+allchars+"]+)\)\)","(ADVP-LOC (ADV \\1-\\2))",currentText)

    # ADVP-DIR
    currentText = re.sub("\(ADVP \(ADV ([Þþ]angað|[Hh]ingað|[Hh]eim|[Áá]leiðis|[Uu]pp|[Nn]iður|[Bb]urt|[Oo]fan|[Þþ]aðan)-(["+allchars+"]+)\)\)","(ADVP-DIR (ADV \\1-\\2))",currentText)

    # Shouldn't really be an ADV at this point, but just in case
    rep("\(ADV sem-sem\)","(C sem-sem)")

    # For some reason there is still a problem with SVO AÐ here, so fix it
    rep("\(PP \(P svo-svo\) \(CP-THT \(C að-að\)\)\)","(PP (P svo-svo) (CP-ADV (C að-að)))")

    #áður, which should be ADVR not ADV
    rep("\(ADV áður-áður\)","(ADVR áður-áður)")
    
    # Fix (VAN Það-þa)
    currentText = re.sub("\(VAN ([Þþ]að)-þa\)", "(NP-SBJ (PRO-N \\1-það))",currentText)

    # Faroese add: VAN vorðnir>RDN

    # Faroese adjectives
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gin)-(['"+allchars+"']+)\)","(ADJ-N \\3-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gið)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gna)-(['"+allchars+"']+)\)","(ADJ-A \\3-egin)")
    rep("\((['"+allchars+"']+) ([Ee]gna)-(['"+allchars+"']+)\)","(ADJ-A \\2-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gnum)-(['"+allchars+"']+)\)","(ADJ-D \\3-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gins)-(['"+allchars+"']+)\)","(ADJ-G \\3-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gnar)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-egin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]gnari)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-egin)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll]ongu)-(['"+allchars+"']+)\)","(ADJ-D \\3-longur)")
    rep("\((['"+allchars+"']+) ([Ll]ongu)-(['"+allchars+"']+)\)","(ADJ-D \\2-longur)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Óó]ndir)-(['"+allchars+"']+)\)","(ADJ-N \\3-óndur)")
    rep("\((['"+allchars+"']+) ([Óó]ndir)-(['"+allchars+"']+)\)","(ADJ-N \\2-óndur)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss])(on\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$num)-(['"+allchars+"']+)\)","(ADJ-D \\3onnum-sannur)")

    # Faroese adverbs
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn])(ið\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$an)-(['"+allchars+"']+)\)","(ADV \\3iðan-niðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff])(ramm\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$an)-(['"+allchars+"']+)\)","(ADV \\3ramman-framman)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) (['"+allchars+"']+liga)-(['"+allchars+"']+)\)","(ADV \\3-\\4)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ldri)-(['"+allchars+"']+)\)","(ADV \\3-aldri)")
    rep("\((['"+allchars+"']+) ([Aa]ldri)-(['"+allchars+"']+)\)","(ADV \\2-aldri)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ltíð)-(['"+allchars+"']+)\)","(ADV \\3-altíð)")
    rep("\((['"+allchars+"']+) ([Aa]ltíð)-(['"+allchars+"']+)\)","(ADV \\2-altíð)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Bb]urtur)-(['"+allchars+"']+)\)","(ADV \\3-burtur)")
    rep("\((['"+allchars+"']+) ([Bb]urtur)-(['"+allchars+"']+)\)","(ADV \\2-burtur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]agar)-(['"+allchars+"']+)\)","(ADV \\3-hagar)")
    rep("\((['"+allchars+"']+) ([Hh]agar)-(['"+allchars+"']+)\)","(ADV \\2-hagar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]igar)-(['"+allchars+"']+)\)","(ADV \\3-higar)")
    rep("\((['"+allchars+"']+) ([Hh]igar)-(['"+allchars+"']+)\)","(ADV \\2-higar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]aðan)-(['"+allchars+"']+)\)","(ADV \\3-haðan)")
    rep("\((['"+allchars+"']+) ([Hh]aðan)-(['"+allchars+"']+)\)","(ADV \\2-haðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]aðani)-(['"+allchars+"']+)\)","(ADV \\3-haðan)")
    rep("\((['"+allchars+"']+) ([Hh]aðani)-(['"+allchars+"']+)\)","(ADV \\2-haðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]iðan)-(['"+allchars+"']+)\)","(ADV \\3-hiðan)")
    rep("\((['"+allchars+"']+) ([Hh]iðan)-(['"+allchars+"']+)\)","(ADV \\2-hiðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]iðani)-(['"+allchars+"']+)\)","(ADV \\3-hiðan)")
    rep("\((['"+allchars+"']+) ([Hh]iðani)-(['"+allchars+"']+)\)","(ADV \\2-hiðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ar)-(['"+allchars+"']+)\)","(ADV \\3-har)")
    rep("\((['"+allchars+"']+) ([Hh]ar)-(['"+allchars+"']+)\)","(ADV \\2-har)")
    rep("\((['"+allchars+"']+) ([Hh]ar)\)","(ADV \\2-har)")
    rep("\(([Hh]ar)-(['"+allchars+"']+)\)","(ADV \\1-har)")
    rep("\(([Hh]ar)\)","(ADV \\1-har)")
    rep("([Hh]ar) (e)","(ADV \\1-har)")
    rep("\(([Hh]ar) (e)\)","(ADV \\1-har)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]er)-(['"+allchars+"']+)\)","(ADV \\3-her)")
    rep("\((['"+allchars+"']+) ([Hh]er)-(['"+allchars+"']+)\)","(ADV \\2-her)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ú)-(['"+allchars+"']+)\)","(ADV \\3-nú)")
    rep("\((['"+allchars+"']+) ([Nn]ú)-(['"+allchars+"']+)\)","(ADV \\2-nú)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]á)-(['"+allchars+"']+)\)","(ADV \\3-tá)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vaðani)-(['"+allchars+"']+)\)","(WADV \\3-hvaðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vaðan)-(['"+allchars+"']+)\)","(WADV \\3-hvaðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]iðan['"+allchars+"']+)-(['"+allchars+"']+)\)","(ADV \\3-hiðan)")
    rep("\((['"+allchars+"']+) ([Hh]iðan['"+allchars+"']+)-(['"+allchars+"']+)\)","(ADV \\2-hiðan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ví)-(['"+allchars+"']+)\)","(WADV \\3-hví)")
    rep("\((['"+allchars+"']+) ([Oo]man)-(['"+allchars+"']+)\)","(ADV \\2-oman)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]man)-(['"+allchars+"']+)\)","(ADV \\3-oman)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]anniliga)-(['"+allchars+"']+)\)","(ADV \\3-sanniliga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]oleiðis)-(['"+allchars+"']+)\)","(WADV \\3-soleiðis)")
    rep("\((['"+allchars+"']+) ([Ss]oleiðis)-(['"+allchars+"']+)\)","(ADV \\2-soleiðis)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Uu]ppaftur)-(['"+allchars+"']+)\)","(ADV \\3-uppaftur)")
    rep("\((['"+allchars+"']+) ([Uu]ppaftur)-(['"+allchars+"']+)\)","(ADV \\2-uppaftur)")

    # Faroese wadverbs
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]var)-(['"+allchars+"']+)\)","(WADV \\3-hvar)")
    rep("\((['"+allchars+"']+) ([Hh]var)-(['"+allchars+"']+)\)","(WADV \\2-hvar)")

    # Faroese modal verbs
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]igur)-(['"+allchars+"']+)\)","(VBPI \\3-eiga)")
    rep("\((['"+allchars+"']+) ([Ee]igur)-(['"+allchars+"']+)\)","(VBPI \\2-eiga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]igi)-(['"+allchars+"']+)\)","(VBPI \\3-eiga)")
    rep("\((['"+allchars+"']+) ([Ee]igi)-(['"+allchars+"']+)\)","(VBPI \\2-eiga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]an)-(['"+allchars+"']+)\)","(MDPI \\3-munna)")
    rep("\((['"+allchars+"']+) ([Mm]an)-(['"+allchars+"']+)\)","(MDPI \\2-munna)")
    rep("\((['"+allchars+"']+) ([Mm]anst)-(['"+allchars+"']+)\)","(MDPI \\2-munna)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]unnu)-(['"+allchars+"']+)\)","(MDPI \\3-munna)")
    rep("\((['"+allchars+"']+) ([Mm]unnu)-(['"+allchars+"']+)\)","(MDPI \\2-munna)")
    rep("\((['"+allchars+"']+) ([Mm]undi)-(['"+allchars+"']+)\)","(MDDS \\2-munna)")
    rep("\((['"+allchars+"']+) ([Mm]unnað)-(['"+allchars+"']+)\)","(MAN \\2-munna)")
    rep("\((['"+allchars+"']+) ([Kk]ann)-(['"+allchars+"']+)\)","(MDPI \\2-kunna)")
    rep("\((['"+allchars+"']+) ([Kk]anst)-(['"+allchars+"']+)\)","(MDPI \\2-kunna)")
    rep("\((['"+allchars+"']+) ([Kk]undi)-(['"+allchars+"']+)\)","(MDDI \\2-kunna)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Kk]undu)-(['"+allchars+"']+)\)","(MDDI \\3-kunna)")
    rep("\((['"+allchars+"']+) ([Kk]undu)-(['"+allchars+"']+)\)","(MDDI \\2-kunna)")
    rep("\((['"+allchars+"']+) ([Kk]unnu)-(['"+allchars+"']+)\)","(MDPI \\2-kunna)")
    rep("\((['"+allchars+"']+) ([Kk]unnað)-(['"+allchars+"']+)\)","(MDN \\2-kunna)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Kk]a)(\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$nn)-(['"+allchars+"']+)\)","(MDPI \\3nn-kunna)")
    rep("\((['"+allchars+"']+) ([Ss]kuldi)-(['"+allchars+"']+)\)","(MDDS \\2-skula)")
    rep("\((['"+allchars+"']+) ([Ss]kuldu)-(['"+allchars+"']+)\)","(MDDS \\2-skula)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]ilt)-(['"+allchars+"']+)\)","(MDPI \\3-vilja)")
    rep("\((['"+allchars+"']+) ([Vv]ilt)-(['"+allchars+"']+)\)","(MDPI \\2-vilja)")

    # Faroese BE
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]óru)-(['"+allchars+"']+)\)","(BEPI \\3-vera)")
    rep("\((['"+allchars+"']+) ([Vv]ar)-(['"+allchars+"']+)\)","(BEDI \\2-vera)")
    rep("\((['"+allchars+"']+) ([Vv]art)-(['"+allchars+"']+)\)","(BEDI \\2-vera)")
    rep("\((['"+allchars+"']+) ([Ee]rt)-(['"+allchars+"']+)\)","(BEPI \\2-vera)")
    rep("\((['"+allchars+"']+) ([Ee]ri)-(['"+allchars+"']+)\)","(BEPI \\2-vera)")
    rep("\((['"+allchars+"']+) ([Ee]r)-(['"+allchars+"']+)\)","(BEPI \\2-vera)")

    # Faroese DO
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]ert)-(['"+allchars+"']+)\)","(DOPI \\3-gera)")
    rep("\((['"+allchars+"']+) ([Gg]ert)-(['"+allchars+"']+)\)","(DOPI \\2-gera)")
    rep("\((['"+allchars+"']+) ([Gg]er)-(['"+allchars+"']+)\)","(DOPI \\2-gera)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]jördi)-(['"+allchars+"']+)\)","(DODI \\3-gera)")
    rep("\((['"+allchars+"']+) ([Gg]jördi)-(['"+allchars+"']+)\)","(DODI \\2-gera)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]jördu)-(['"+allchars+"']+)\)","(DODI \\3-gera)")
    rep("\((['"+allchars+"']+) ([Gg]jördu)-(['"+allchars+"']+)\)","(DODI \\2-gera)")

    # Faroese RD
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]órðu)-(['"+allchars+"']+)\)","(RDDI \\3-verða)")
    rep("\((['"+allchars+"']+) ([Vv]órðu)-(['"+allchars+"']+)\)","(RDDI \\2-verða)")

    # Faroese HV
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ava)-(['"+allchars+"']+)\)","(HVPI \\3-hava)")
    rep("\((['"+allchars+"']+) ([Hh]ava)-(['"+allchars+"']+)\)","(HVPI \\2-hava)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]avt)-(['"+allchars+"']+)\)","(HVN \\3-hava)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]evur)-(['"+allchars+"']+)\)","(HVPI \\3-hava)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]avi)-(['"+allchars+"']+)\)","(HVPI \\3-hava)")
    rep("\((['"+allchars+"']+) ([Hh]avi)-(['"+allchars+"']+)\)","(HVPI \\2-hava)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]övdu)-(['"+allchars+"']+)\)","(HVDI \\3-hava)")
    rep("\((['"+allchars+"']+) ([Hh]övdu)-(['"+allchars+"']+)\)","(HVDI \\2-hava)")
    rep("\((['"+allchars+"']+) ([Hh]ava)-(['"+allchars+"']+)\)","(HVPI \\2-hava)")
    rep("\((['"+allchars+"']+) ([Hh]evði)-(['"+allchars+"']+)\)","(HVDI \\2-hava)")

    # Faroese VAN, RDN etc.
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Áá]ðr)(enn)-(['"+allchars+"']+)\)","(ADVR \\3$-áðr) (P $\\4-enn)")
    rep("\((['"+allchars+"']+) ([Oo]rð)(ið)-(['"+allchars+"']+)\)","(N-N \\2$-orð) (D-N $\\3-hinn)")
    rep("\(VAN ([Oo])rðið-orða\)","(N-N \\1rðið-orð)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]orð\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) \$(['"+allchars+"']+)-(['"+allchars+"']+)\)","(RDN vorð\\7-verða)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]orð['"+allchars+"']+)-(['"+allchars+"']+)\)","(RDN \\3-verða)")

    currentText = re.sub("\((NP|NP-OB2) \(N-[NADG] ([Tt]á)-(tá)\)\)","(ADVP-TMP (ADV \\2-\\3))",currentText)
#    currentText = re.sub("\((NP|NP-OB2|NP-OB1) \(CODE VS["+allchars+"]+\) \(N-[NADG] ([Tt]á)-(tá)\)\)","(ADVP-TMP (ADV \\2-\\3))",currentText)
    currentText = re.sub("\(ADJP \(ADJ-([NADG]) ([Tt]á)ið-táinn\)\)", "(ADVP-TMP (ADV \\2$-tá) (C $ið-ið))",currentText)
#    currentText = re.sub("\(['"+allchars+"']+ \(['"+allchars+"']+ ([Tt]á)-['"+allchars+"']+\)\) \(['"+allchars+"']+ \(['"+allchars+"']+-['"+allchars+"']+ ([Ii]ð)-['"+allchars+"']+\)\)" , "(ADV \\1-tá) (C \\2-ið)",currentText)

    # Faroese OTHER
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ðrar)-(['"+allchars+"']+)\)","(OTHERS-N \\3-annar)")
    rep("\((['"+allchars+"']+) ([Aa]ðrar)-(['"+allchars+"']+)\)","(OTHERS-N \\2-annar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ðrir)-(['"+allchars+"']+)\)","(OTHERS-N \\3-annar)")
    rep("\((['"+allchars+"']+) ([Aa]ðrir)-(['"+allchars+"']+)\)","(OTHERS-N \\2-annar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ðra)-(['"+allchars+"']+)\)","(OTHERS-A \\3-annar)")
    rep("\((['"+allchars+"']+) ([Aa]ðra)-(['"+allchars+"']+)\)","(OTHERS-A \\2-annar)")

    # Faroese pronouns
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ú)-(['"+allchars+"']+)\)","(PRO-N \\3-tú)")
#    rep("\((NPR)-([NADG]) ([Tt]ú)-(tús)\)","(PRO-N \\3-tú)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]g)-(['"+allchars+"']+)\)","(PRO-N \\3-eg)")
    rep("\(PRO-N eg-(ég)\)","(PRO-N eg-eg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]it)-(['"+allchars+"']+)\)","(PRO-N \\3-eg)")
    rep("\((['"+allchars+"']+) ([Vv]it)-(['"+allchars+"']+)\)","(PRO-N \\2-eg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]it)-(['"+allchars+"']+)\)","(PRO-N \\3-tú)")
    rep("\((['"+allchars+"']+) ([Tt]it)-(['"+allchars+"']+)\)","(PRO-N \\2-tú)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]kkum)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-eg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ykkum)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-tú)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]eg)-(['"+allchars+"']+)\)","(PRO-A \\3-eg)")
    rep("\((['"+allchars+"']+) ([Mm]eg)-(['"+allchars+"']+)\)","(PRO-A \\2-eg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]eg)-(['"+allchars+"']+)\)","(PRO-A \\3-tú)")
    rep("\((['"+allchars+"']+) ([Tt]eg)-(['"+allchars+"']+)\)","(PRO-A \\2-tú)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]eg)-(['"+allchars+"']+)\)","(PRO-A \\3-seg)")
    rep("\((['"+allchars+"']+) ([Ss]eg)-(['"+allchars+"']+)\)","(PRO-A \\2-seg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]ær)-(['"+allchars+"']+)\)","(PRO-D \\3-eg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ær)-(['"+allchars+"']+)\)","(PRO-D \\3-tú)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ær)-(['"+allchars+"']+)\)","(PRO-D \\3-seg)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) (Hann)-(hann)\)","(PRO-\\2 \\3-\\4)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]on)-(['"+allchars+"']+)\)","(PRO-N \\3-hon)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ana)-(['"+allchars+"']+)\)","(PRO-A \\3-hon)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ennara)-(['"+allchars+"']+)\)","(PRO-G \\3-hon)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ansara)-(['"+allchars+"']+)\)","(PRO-G \\3-hann)")
    rep("\((['"+allchars+"']+) ([Hh]ansara)-(hansara)\)","(PRO-G \\2-hann)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]kkara)-(['"+allchars+"']+)\)","(PRO-G \\3-okkara)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Yy]kkara)-(['"+allchars+"']+)\)","(PRO-G \\3-ykkara)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ykkara)-(['"+allchars+"']+)\)","(PRO-G \\3-tykkara)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]að)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-tað)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]í)-(['"+allchars+"']+)\)","(PRO-D \\3-tað)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ess)-(['"+allchars+"']+)\)","(PRO-G \\3-tað)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]eir)-(['"+allchars+"']+)\)","(PRO-N \\3-hann)")
    rep("\((['"+allchars+"']+) ([Tt]eir)-(['"+allchars+"']+)\)","(PRO-N \\2-hann)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]eimum)-(['"+allchars+"']+)\)","(PRO-D \\3-hann)")
    rep("\((['"+allchars+"']+) ([Tt]eimum)-(['"+allchars+"']+)\)","(PRO-D \\2-hann)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]eirra)-(['"+allchars+"']+)\)","(PRO-G \\3-hann)")
    rep("\((['"+allchars+"']+) ([Tt]eirra)-(['"+allchars+"']+)\)","(PRO-G \\2-hann)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ey)-(['"+allchars+"']+)\)","(PRO-N \\3-tað)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]ítt)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-mín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ítt)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-tín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ítt)-(['"+allchars+"']+)\)","(PRO-\\2 \\3-sín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]íni)-(['"+allchars+"']+)\)","(PRO-D \\3-mín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ín)-(['"+allchars+"']+)\)","(PRO-N \\3-tín)")
    rep("\((['"+allchars+"']+) ([Tt]ín)-(['"+allchars+"']+)\)","(PRO-N \\2-tín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]íni)-(['"+allchars+"']+)\)","(PRO-D \\3-tín)")
    rep("\((['"+allchars+"']+) ([Tt]íni)-(['"+allchars+"']+)\)","(PRO-N \\2-tín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ínir)-(['"+allchars+"']+)\)","(PRO-N \\3-tín)")
    rep("\((['"+allchars+"']+) ([Tt]ínir)-(['"+allchars+"']+)\)","(PRO-N \\2-tín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]íni)-(['"+allchars+"']+)\)","(PRO-D \\3-sín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]ínari)-(['"+allchars+"']+)\)","(PRO-D \\3-mín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ínari)-(['"+allchars+"']+)\)","(PRO-D \\3-tín)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ínari)-(['"+allchars+"']+)\)","(PRO-D \\3-sín)")

    # Faroese pronouns (other pronouns)
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvur)-(["+allchars+"]+)\)","(PRO-N \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvir)-(["+allchars+"]+)\)","(PRO-N \\3-sjálvur)")
    rep("\((['"+allchars+"']+) ([Ss]jálvir)-(["+allchars+"]+)\)","(PRO-N \\2-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss])(jálv\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$an)-(['"+allchars+"']+)\)","(PRO-A \\3jálvan-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvan)-(["+allchars+"]+)\)","(PRO-A \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvum)-(["+allchars+"]+)\)","(PRO-D \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvs)-(["+allchars+"]+)\)","(PRO-G \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálv)-(["+allchars+"]+)\)","(PRO-N \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvar)-(["+allchars+"]+)\)","(PRO-N \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvt)-(["+allchars+"]+)\)","(PRO-N \\3-sjálvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jálvari)-(["+allchars+"]+)\)","(PRO-D \\3-sjálvur)")

    # Faroese prepositions
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]v)-(['"+allchars+"']+)\)","(P \\3-av)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]v)(stað)-(['"+allchars+"']+)\)","(P \\3$-av) (N-D $\\4-staður)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]man)(frá)-(['"+allchars+"']+)\)","(ADV \\3$-oman) (P $\\4-frá)")
    rep("\((['"+allchars+"']+) ([Oo]man)(frá)-(['"+allchars+"']+)\)","(ADV \\2$-oman) (P $\\3-frá)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]yri)-(['"+allchars+"']+)\)","(P \\3-fyri)")
    rep("\((['"+allchars+"']+) ([Ff]yri)-(['"+allchars+"']+)\)","(P \\2-fyri)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]jögnum)-(['"+allchars+"']+)\)","(P \\3-gjögnum)")
    rep("\((['"+allchars+"']+) ([Gg]jögnum)-(['"+allchars+"']+)\)","(P \\2-gjögnum)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]illum)-(['"+allchars+"']+)\)","(P \\3-millum)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Íí])(millum)-(['"+allchars+"']+)\)","(P \\3$-í) (P $\\4-millum)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Áá])(millum)-(['"+allchars+"']+)\)","(P \\3$-á) (P $\\4-millum)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Íí])(móti)-(['"+allchars+"']+)\)","(P \\3$-í) (N-D $\\4-móti)")
    rep("\((['"+allchars+"']+) ([Íí])(móti)-(['"+allchars+"']+)\)","(P \\2$-í) (N-D $\\3-móti)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Íí])(mót)-(['"+allchars+"']+)\)","(P \\3$-í) (N-D $\\4-móti)")
    rep("\((['"+allchars+"']+) ([Íí])(mót)-(['"+allchars+"']+)\)","(P \\2$-í) (N-D $\\3-móti)")
    rep("\((ADV) ([Uu]m)-(['"+allchars+"']+)\)","(P \\2-um)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]ið)-(['"+allchars+"']+)\)","(P \\3-við)")
    rep("\((['"+allchars+"']+) ([Yy]vir)-(['"+allchars+"']+)\)","(P \\2-yvir)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Uu]pp)(um)-(['"+allchars+"']+)\)","(RP \\3$-upp) (P $\\4-um)")
    rep("\((['"+allchars+"']+) ([Uu]pp)(um)-(['"+allchars+"']+)\)","(RP \\2$-upp) (P $\\3-um)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Uu]ttan)-(['"+allchars+"']+)\)","(P \\3-uttan)")
    rep("\((['"+allchars+"']+) ([Uu]ttan)-(['"+allchars+"']+)\)","(P \\2-uttan)")

    # Faroese RP and FP
    rep("\((ADV) ([Ff]yri)-(['"+allchars+"']+)\)","(RP \\2-fyri)")
    rep("\((ADV) ([Tt]il)-(['"+allchars+"']+)\)","(RP \\2-til)")
    rep("\((ADV) ([Uu]m)-(['"+allchars+"']+)\)","(RP \\2-um)")
    rep("\((ADV) ([Uu]pp)-(['"+allchars+"']+)\)","(RP \\2-upp)")
    rep("\((ADV) ([Úú]t)-(['"+allchars+"']+)\)","(RP \\2-út)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]iður)(í)-(['"+allchars+"']+)\)","(RP \\3$-niður) (RPX $\\4-í)")
    rep("\((['"+allchars+"']+) ([Nn]iður)(í)-(['"+allchars+"']+)\)","(RP \\2$-niður) (RPX $\\3-í)")
    rep("\((['"+allchars+"']+) ([Bb]ert)-(['"+allchars+"']+)\)","(FP \\2-bert)")

    # Faroese determiners
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh])(es\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$in)-(['"+allchars+"']+)\)","(D-\\2 \\3esin-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]esin)-(['"+allchars+"']+)\)","(D-N \\3-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]esi)-(['"+allchars+"']+)\)","(D-N \\3-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]esum)-(['"+allchars+"']+)\)","(D-D \\3-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]endan)-(['"+allchars+"']+)\)","(D-A \\3-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]etta)-(['"+allchars+"']+)\)","(D-N \\3-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]esa)-(['"+allchars+"']+)\)","(D-A \\3-hesin)")
    rep("\((['"+allchars+"']+) ([Hh]esa)-(['"+allchars+"']+)\)","(D-A \\2-hesin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]a)(\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$nn)-(['"+allchars+"']+)\)","(D-\\2 \\3nn-tann)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ann)-(['"+allchars+"']+)\)","(D-N \\3-tann)")

    # Faroese quantifiers
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]lt)-(['"+allchars+"']+)\)","(Q-\\2 \\3-allur)")
    rep("\((['"+allchars+"']+) ([Aa]lt)-(['"+allchars+"']+)\)","(Q-N \\2-allur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ll)-(['"+allchars+"']+)\)","(Q-N \\3-allur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]llum)-(['"+allchars+"']+)\)","(Q-D \\3-allur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]llari)-(['"+allchars+"']+)\)","(Q-D \\3-allur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]ls)-(['"+allchars+"']+)\)","(Q-G \\3-allur)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]ingin)-(['"+allchars+"']+)\)","(Q-N \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]ingir)-(['"+allchars+"']+)\)","(Q-N \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]ngan)-(['"+allchars+"']+)\)","(Q-A \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]ngum)-(['"+allchars+"']+)\)","(Q-D \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]ngar)-(['"+allchars+"']+)\)","(Q-\\2 \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]ngari)-(['"+allchars+"']+)\)","(Q-D \\3-eingin)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]inki)-(['"+allchars+"']+)\)","(Q-\\2 \\3-einki)")
    rep("\((['"+allchars+"']+) ([Ee]inki)-(['"+allchars+"']+)\)","(Q-N \\2-einki)")
    rep("\((['"+allchars+"']+) ([Ee]inkis)-(['"+allchars+"']+)\)","(Q-G \\2-einki)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkur)-(['"+allchars+"']+)\)","(Q-N \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkur)-(['"+allchars+"']+)\)","(Q-N \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkran)-(['"+allchars+"']+)\)","(Q-A \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkran)-(['"+allchars+"']+)\)","(Q-A \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkurn)-(['"+allchars+"']+)\)","(Q-A \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkurn)-(['"+allchars+"']+)\)","(Q-A \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkrum)-(['"+allchars+"']+)\)","(Q-D \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkrum)-(['"+allchars+"']+)\)","(Q-D \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkurs)-(['"+allchars+"']+)\)","(Q-G \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkurs)-(['"+allchars+"']+)\)","(Q-G \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkra)-(['"+allchars+"']+)\)","(Q-A \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkra)-(['"+allchars+"']+)\)","(Q-A \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkrari)-(['"+allchars+"']+)\)","(Q-D \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkrari)-(['"+allchars+"']+)\)","(Q-D \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]kkurt)-(['"+allchars+"']+)\)","(Q-N \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]kkurt)-(['"+allchars+"']+)\)","(Q-N \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkrir)-(['"+allchars+"']+)\)","(Q-N \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkrir)-(['"+allchars+"']+)\)","(Q-N \\2-onkur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Oo]nkrar)-(['"+allchars+"']+)\)","(Q-N \\3-onkur)")
    rep("\((['"+allchars+"']+) ([Oo]nkrar)-(['"+allchars+"']+)\)","(Q-N \\2-onkur)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akar)-(['"+allchars+"']+)\)","(Q-N \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akran)-(['"+allchars+"']+)\)","(Q-A \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ökrum)-(['"+allchars+"']+)\)","(Q-D \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ökur)-(['"+allchars+"']+)\)","(Q-N \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akra)-(['"+allchars+"']+)\)","(Q-A \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akrari)-(['"+allchars+"']+)\)","(Q-D \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akað)-(['"+allchars+"']+)\)","(Q-N \\3-nakar)")
    rep("\((['"+allchars+"']+) ([Nn]akað)-(['"+allchars+"']+)\)","(Q-N \\2-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ökrum)-(['"+allchars+"']+)\)","(Q-D \\3-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akrir)-(['"+allchars+"']+)\)","(Q-N \\3-nakar)")
    rep("\((['"+allchars+"']+) ([Nn]akrir)-(['"+allchars+"']+)\)","(Q-N \\2-nakar)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]akrar)-(['"+allchars+"']+)\)","(Q-N \\3-nakar)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angur)-(['"+allchars+"']+)\)","(Q-N \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]ongum)-(['"+allchars+"']+)\)","(Q-D \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]ong)-(['"+allchars+"']+)\)","(Q-N \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angir)-(['"+allchars+"']+)\)","(Q-N \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angar)-(['"+allchars+"']+)\)","(Q-\\2 \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angari)-(['"+allchars+"']+)\)","(Q-D \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angs)-(['"+allchars+"']+)\)","(Q-G \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angrar)-(['"+allchars+"']+)\)","(Q-G \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angra)-(['"+allchars+"']+)\)","(Q-G \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]angt)-(['"+allchars+"']+)\)","(Q-\\2 \\3-mangur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ógv)-(['"+allchars+"']+)\)","(Q-\\2 \\3-nógvur)")
    rep("\((['"+allchars+"']+) ([Nn]ógv)-(['"+allchars+"']+)\)","(Q-\\1 \\2-nógvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ógvur)-(['"+allchars+"']+)\)","(Q-N \\3-nógvur)")
    rep("\((['"+allchars+"']+) ([Nn]ógvur)-(['"+allchars+"']+)\)","(Q-N \\2-nógvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ógvan)-(['"+allchars+"']+)\)","(Q-A \\3-nógvur)")
    rep("\((['"+allchars+"']+) ([Nn]ógvan)-(['"+allchars+"']+)\)","(Q-A \\2-nógvur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ógvum)-(['"+allchars+"']+)\)","(Q-D \\3-nógvur)")
    rep("\((['"+allchars+"']+) ([Nn]ógvum)-(['"+allchars+"']+)\)","(Q-D \\2-nógvur)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ummur)-(['"+allchars+"']+)\)","(Q-N \\3-summur)")
    rep("\((['"+allchars+"']+) ([Ss]ummur)-(['"+allchars+"']+)\)","(Q-N \\2-summur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]umm)-(['"+allchars+"']+)\)","(Q-N \\3-summur)")
    rep("\((['"+allchars+"']+) ([Ss]umm)-(['"+allchars+"']+)\)","(Q-N \\2-summur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ummar)-(['"+allchars+"']+)\)","(Q-N \\3-summur)")
    rep("\((['"+allchars+"']+) ([Ss]ummar)-(['"+allchars+"']+)\)","(Q-N \\2-summur)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ummir)-(['"+allchars+"']+)\)","(Q-N \\3-summur)")
    rep("\((['"+allchars+"']+) ([Ss]ummir)-(['"+allchars+"']+)\)","(Q-N \\2-summur)")

    # Faroese negation
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ii]kki)-(['"+allchars+"']+)\)","(NEG \\3-ikki)")
    rep("\((['"+allchars+"']+) ([Ii]kki)-(['"+allchars+"']+)\)","(NEG \\2-ikki)")

    # Faroese also
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]isini)-(['"+allchars+"']+)\)","(ALSO \\3-eisini)")
    rep("\((['"+allchars+"']+) ([Ee]isini)-(['"+allchars+"']+)\)","(ALSO \\2-eisini)")

    # Faroese complementizers
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Áá]ðr)(enn)-(['"+allchars+"']+)\)","(ADVR \\3$-áðr) (P $\\4-enn)")
    rep("\((FW) (so)-(so)\)","(P \\2-\\3)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ii]ð)-(['"+allchars+"']+)\)","(C \\3-ið)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]um)-(['"+allchars+"']+)\)","(C \\3-sum)")
    rep("\((FW) ([Aa]t)-(['"+allchars+"']+)\)","(C \\2-at)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Aa]t)-(['"+allchars+"']+)\)","(C \\3-at)")

    # Faroese INTJ
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ei)-(nei)\)","(INTJ \\3-\\4)")
    rep("\((ADJ)-([NADG]) (['"+allchars+"']+)(in)-(['"+allchars+"']+)\)","(N-\\2 \\3$-\\3) (D-\\2 $\\4-hinn)")

    # Faroese conjunctions
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Mm]en)-(men)\)","(CONJ \\3-\\4)")

    # Faroese numbers, cardinal
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]vey)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tveir)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]veimum)-(['"+allchars+"']+)\)","(NUM-D \\3-tveir)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ríggir|[Tt]ríggjar|[Tt]rý|)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tríggir)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]rimum)-(['"+allchars+"']+)\)","(NUM-D \\3-tríggir)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]ýra)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-fýra)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]eks)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-seks)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jey)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-sjey)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]íggju)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-níggju)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]íggju)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tíggju)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]llivu)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-ellivu)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ólv)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tólv)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]rettan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-trettan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]júrtan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-fjúrtan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]imtan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-fimtan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ekstan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-sekstan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]eytjan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-seytjan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Áá]tjan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-átjan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]ítjan)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-nítjan)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]júgu)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tjúgu)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ríati)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-tríati)")
    rep("\((['"+allchars+"']+) ([Tt]ríati)-(['"+allchars+"']+)\)","(NUM-N \\2-tríati)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]jöruti)-(['"+allchars+"']+)\)","(NUM-\\2 \\3-fjöruti)")

    # Faroese numbers, ordinal
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]riðja|[Tt]riði)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-triði)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]jórða|[Ff]jórði)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-fjórði)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]imta|[Ff]imti|[Ff]immta|[Ff]immti)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-fimti)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ætta|[Ss]ætti)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-sætti)")
    rep("\((['"+allchars+"']+) ([Ss]ætta)-(['"+allchars+"']+)\)","(ADJ-A \\2-sætti)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]jeynda|[Ss]jeyndi)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-sjeyndi)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Áá]ttandi|[Áá]ttanda|[Áá]ttundi|[Áá]ttunda)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-áttandi)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Nn]íggjunda|[Nn]íggjundi)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-níggjundi)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]íggjunda|[Tt]íggjundi)-(['"+allchars+"']+)\)","(ADJ-\\2 \\3-tíggjundi)")

    # Faroese wh
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vussu)-(['"+allchars+"']+)\)","(WADV \\3-hvussu)")
    rep("\((['"+allchars+"']+) ([Hh]vussu)-(['"+allchars+"']+)\)","(WADV \\2-hvussu)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vat)-(['"+allchars+"']+)\)","(WPRO-\\2 \\3-hvör)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vör)-(['"+allchars+"']+)\)","(WPRO-N \\3-hvör)")
    rep("\((['"+allchars+"']+) ([Hh]vör)-(['"+allchars+"']+)\)","(WPRO-N \\2-hvör)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vörn)-(['"+allchars+"']+)\)","(WPRO-A \\3-hvör)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vörjum)-(['"+allchars+"']+)\)","(WPRO-D \\3-hvör)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]vörs)-(['"+allchars+"']+)\)","(WPRO-G \\3-hvör)")

    # Faroese lexicon, oblique subject verbs
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ungra)-(['"+allchars+"']+)\)","(VBPI \\3-hungra)")
    rep("\((['"+allchars+"']+) ([Hh]ungra)-(['"+allchars+"']+)\)","(VBPI \\2-hungra)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]ysta)-(['"+allchars+"']+)\)","(VBPI \\3-tysta)")
    rep("\((['"+allchars+"']+) ([Tt]ysta)-(['"+allchars+"']+)\)","(VBPI \\2-tysta)")

    # Faroese lexicon, strong verbs
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Bb]óru)-(['"+allchars+"']+)\)","(VBDI \\3-bera)")
    rep("\((['"+allchars+"']+) ([Bb]óru)-(['"+allchars+"']+)\)","(VBDI \\2-bera)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Dd])(rip\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$ið)-(['"+allchars+"']+)\)","(VBN \\3ipið-drepa)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Dd])(rip\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$in)-(['"+allchars+"']+)\)","(VBN \\3ipin-drepa)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Dd]rópu)-(['"+allchars+"']+)\)","(VBDI \\3-drepa)")
    rep("\((['"+allchars+"']+) ([Dd]rópu)-(['"+allchars+"']+)\)","(VBDI \\2-drepa)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Dd]rupu)-(['"+allchars+"']+)\)","(VBDI \\3-drepa)")
    rep("\((['"+allchars+"']+) ([Dd]rupu)-(['"+allchars+"']+)\)","(VBDI \\2-drepa)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]itur)-(['"+allchars+"']+)\)","(VBPI \\3-eita)")
    rep("\((['"+allchars+"']+) ([Ee]itur)-(['"+allchars+"']+)\)","(VBPI \\2-eita)")
    rep("\((['"+allchars+"']+) ([Ææ]t)-(['"+allchars+"']+)\)","(VBDI \\2-eita)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Óó]tu)-(['"+allchars+"']+)\)","(VBDI \\3-eta)")
    rep("\((['"+allchars+"']+) ([Óó]ótu)-(['"+allchars+"']+)\)","(VBDI \\2-eta)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]ell)-(['"+allchars+"']+)\)","(VBDI \\3-falla)")
    rep("\((['"+allchars+"']+) ([Ff]ell)-(['"+allchars+"']+)\)","(VBDI \\2-falla)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]ar)-(['"+allchars+"']+)\)","(VBI \\3-fara)")
    rep("\((['"+allchars+"']+) ([Ff]ar)-(['"+allchars+"']+)\)","(VBI \\2-fara)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]áa)-(['"+allchars+"']+)\)","(VB \\3-fáa)")
    rep("\((['"+allchars+"']+) ([Ff]áa)-(['"+allchars+"']+)\)","(VB \\2-fáa)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]ingið)-(['"+allchars+"']+)\)","(VBN \\3-fáa)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ff]ekk)-(['"+allchars+"']+)\)","(VBDI \\3-fáa)")
    rep("\((['"+allchars+"']+) ([Ff]ekk)-(['"+allchars+"']+)\)","(VBDI \\2-fáa)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg])(ing\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$in)-(['"+allchars+"']+)\)","(VBN \\3ingin-ganga)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]ev)-(['"+allchars+"']+)\)","(VBI \\3-geva)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]eva)-(['"+allchars+"']+)\)","(VBPI \\3-geva)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]evur)-(['"+allchars+"']+)\)","(VBPI \\3-geva)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]av)-(['"+allchars+"']+)\)","(VBDI \\3-geva)")
    rep("\((['"+allchars+"']+) ([Gg]av)-(['"+allchars+"']+)\)","(VBDI \\2-geva)")
    rep("\((['"+allchars+"']+) ([Gg]óvu)-(['"+allchars+"']+)\)","(VBDI \\2-geva)")
    rep("\((['"+allchars+"']+) ([Gg]ivin)-(['"+allchars+"']+)\)","(VAN \\2-geva)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]ivin)-(['"+allchars+"']+)\)","(VAN \\3-geva)")
    rep("\((['"+allchars+"']+) ([Gg]ivið)-(['"+allchars+"']+)\)","(VBN \\2-geva)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ildið)-(['"+allchars+"']+)\)","(VBN \\3-halda)")
    rep("\((['"+allchars+"']+) ([Hh]ildið)-(['"+allchars+"']+)\)","(VBN \\2-halda)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]ildu)-(['"+allchars+"']+)\)","(VBDI \\3-halda)")
    rep("\((['"+allchars+"']+) ([Hh]ildu)-(['"+allchars+"']+)\)","(VBDI \\2-halda)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Hh]elt)-(['"+allchars+"']+)\)","(VBDI \\3-halda)")
    rep("\((['"+allchars+"']+) ([Hh]elt)-(['"+allchars+"']+)\)","(VBDI \\2-halda)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll]atið)-(['"+allchars+"']+)\)","(VBPI \\3-láta)")
    rep("\((['"+allchars+"']+) ([Ll]atið)-(['"+allchars+"']+)\)","(VBPI \\2-láta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll])(at\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$ið)-(['"+allchars+"']+)\)","(VBN \\3atið-láta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll]ótu)-(['"+allchars+"']+)\)","(VBDI \\3-láta)")
    rep("\((['"+allchars+"']+) ([Ll]ótu)-(['"+allchars+"']+)\)","(VBDI \\2-láta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll]æt)-(['"+allchars+"']+)\)","(VBDI \\3-láta)")
    rep("\((['"+allchars+"']+) ([Ll]æt)-(['"+allchars+"']+)\)","(VBDI \\2-láta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ll]etur)-(['"+allchars+"']+)\)","(VBPI \\3-láta)")
    rep("\((['"+allchars+"']+) ([Ll]etur)-(['"+allchars+"']+)\)","(VBPI \\2-láta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Kk]omu)-(['"+allchars+"']+)\)","(VBDI \\3-koma)")
    rep("\((['"+allchars+"']+) ([Kk]omu)-(['"+allchars+"']+)\)","(VBDI \\2-koma)")
    rep("\((['"+allchars+"']+) ([Ss]æð)-(['"+allchars+"']+)\)","(VBN \\2-síggja)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]æð)-(['"+allchars+"']+)\)","(VBN \\3-síggja)")
    rep("\((['"+allchars+"']+) ([Ss]egði)-(['"+allchars+"']+)\)","(VBDI \\2-siga)")
    rep("\((['"+allchars+"']+) ([Ss]igi)-(['"+allchars+"']+)\)","(VBPI \\2-siga)")
    rep("\((['"+allchars+"']+) ([Ss]ögdu)-(['"+allchars+"']+)\)","(VBDI \\2-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ögdu)-(['"+allchars+"']+)\)","(VBDI \\3-siga)")
    rep("\((['"+allchars+"']+) ([Ss]agdi)-(['"+allchars+"']+)\)","(VBDI \\2-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]agdi)-(['"+allchars+"']+)\)","(VBDI \\3-siga)")
    rep("\((['"+allchars+"']+) ([Ss]igur)-(['"+allchars+"']+)\)","(VBPI \\2-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]igur)-(['"+allchars+"']+)\)","(VBPI \\3-siga)")
    rep("\((['"+allchars+"']+) ([Ss]agdur)-(['"+allchars+"']+)\)","(VAN \\2-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]agdur)-(['"+allchars+"']+)\)","(VAN \\3-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]íggj)-(['"+allchars+"']+)\)","(VBI \\3-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]ígg)(\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$ið)-(['"+allchars+"']+)\)","(VBPI \\3ið-siga)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]óu)-(['"+allchars+"']+)\)","(VBPI \\3-siga)")
    rep("\((['"+allchars+"']+) ([Ss]óu)-(['"+allchars+"']+)\)","(VBPI \\2-siga)")
    rep("\((['"+allchars+"']+) ([Ss]purdu)-(['"+allchars+"']+)\)","(VBDI \\2-spyrja)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]purdu)-(['"+allchars+"']+)\)","(VBN \\3-spyrja)")
    rep("\((['"+allchars+"']+) ([Ss]purdi)-(['"+allchars+"']+)\)","(VBDI \\2-spyrja)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ss]purdi)-(['"+allchars+"']+)\)","(VBN \\3-spyrja)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt])(ik\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$in)-(['"+allchars+"']+)\)","(VAN \\3ikin-taka)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt])(ik\$)-(['"+allchars+"']+)\) \((['"+allchars+"']+)-(['"+allchars+"']+) (\$ið)-(['"+allchars+"']+)\)","(VBN \\3ikið-taka)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]reyt)-(['"+allchars+"']+)\)","(VBDI \\3-tróta)")
    rep("\((['"+allchars+"']+) ([Tt]reyt)-(['"+allchars+"']+)\)","(VBDI \\2-tróta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]rutu)-(['"+allchars+"']+)\)","(VBDI \\3-tróta)")
    rep("\((['"+allchars+"']+) ([Tt]rutu)-(['"+allchars+"']+)\)","(VBDI \\2-tróta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]rotið)-(['"+allchars+"']+)\)","(VBN \\3-tróta)")
    rep("\((['"+allchars+"']+) ([Tt]rotið)-(['"+allchars+"']+)\)","(VBN \\2-tróta)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Tt]rýr)-(['"+allchars+"']+)\)","(VBPI \\3-trúgva)")
    rep("\((['"+allchars+"']+) ([Tt]rýr)-(['"+allchars+"']+)\)","(VBPI \\2-trúgva)")

    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Vv]ita)-(['"+allchars+"']+)\)","(VBPI \\3-vita)")
    rep("\((['"+allchars+"']+) ([Vv]ita)-(['"+allchars+"']+)\)","(VBPI \\2-vita)")

    # Faroese lexicon, nouns
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Dd]ag)(in)-(['"+allchars+"']+)\)","(N-A \\3$-dagur) (D-A $\\4-hinn)")
    rep("\((['"+allchars+"']+) ([Dd]ag)(in)-(['"+allchars+"']+)\)","(N-A \\2$-orð) (D-A $\\3-hinn)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Ee]yg)(uni)-(['"+allchars+"']+)\)","(NS-N \\3$-eyga) (D-N $\\4-hinn)")
    rep("\((['"+allchars+"']+) ([Ee]yg)(uni)-(['"+allchars+"']+)\)","(NS-N \\2$-eyga) (D-N $\\3-hinn)")
    rep("\(N-([A-Z]) (Gud["+allchars+"]+)-(gud)\)","(NPR-\\1 \\2-\\3)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Jj]esus)-(['"+allchars+"']+)\)","(NPR-N \\3-jesus)")
    rep("\((N)-([A-Z]) (Jesu["+allchars+"]+)-jesusur\)","(NPR-\\2 \\3-jesus)")
    rep("\(NPR-([A-Z]) (Jesu["+allchars+"]+)-jesuur\)","(NPR-\\1 \\2-jesus)")
    rep("\(NPR-([A-Z]) (Jesu["+allchars+"]+)-jesusur\)","(NPR-\\1 \\2-jesus)")
    rep("\((ADJ)-([A-Z]) (Jesu["+allchars+"]+)-jesus\)","(NPR-\\2 \\3-jesus)")
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Gg]uð)(['"+allchars+"']+)-(['"+allchars+"']+)\)","(NPR-\\2 \\3\\4-guð)")
    rep("\((['"+allchars+"']+) ([Rr]abbi)-(['"+allchars+"']+)\)","(N-N \\2-rabbi)")

    # Faroese word forms that trigger errors
    rep("\((['"+allchars+"']+)-(['"+allchars+"']+) ([Kk]ennir)-(['"+allchars+"']+)\)","(VBPI \\3-kenna)")
    rep("\((['"+allchars+"']+) ([Kk]ennir)-(['"+allchars+"']+)\)","(VBPI \\2-kenna)")

# Start script
# Load input file (ipsd)
f = open(sys.argv[1]+".ipsdx", 'r')
currentText = f.read()

load_lemmas() # ... into the lemmas dictionary
remove_extra_ipsd_stuff() # ... like TIMEX
convert_iceparser_functions() # ... like NP-SBJ
convert_brackets_to_pars() # just simple "[" to "(" conversion
parenthesize_punctuation() # before this command those do not have their own pars

# Fix foreign word "bug" and similar stuff
currentText = re.sub("\n(["+allchars+"]+) e\n","\n(e \\1)\n",currentText)
currentText = re.sub("\nað cn\n","\n(cn að)\n",currentText)
currentText = re.sub("\n(["+allchars+"]+) ft([a-z123]+)\n","\n(WPRO \\1)\n",currentText)

make_tag_word_pars()
add_ip_mat()
convert_phrase_labels()
#split_determiners()
convert_tags_to_icepahc()
replace_special_verb_tags()
final_replacements()

rep("\([,;\.:?!] ([,;\.:?!]-[,;\.:?!][\)]+\n\n)","(. \\1")

# Write result to output file
f = open(sys.argv[1]+".ipsd", 'w')
f.write(currentText)
f.close()

