copy_corpus:t

node:IP*
query: (IP* idoms NP*|ADVP*) AND (ADVP* idoms ADV) AND (ADV idomsonly tá*-tá|Tá-tá) AND (ADVP* iprecedes NP*) AND ({1}NP* idoms *-N|*-A|*-D|*-G) AND ({2}*-N idoms ið-*)

replace_label{1}: CP-REL
replace_label{2}: C
