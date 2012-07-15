copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}NP-SBJ|NP-OB1|NP-OB2 idoms PRO-*) AND (PRO-* idoms mítt|Mítt|títt|Títt|sítt|Sítt|tínir|Tínir|tínar|Tínar|tín|Tín)

replace_label{1}: NP-POS
