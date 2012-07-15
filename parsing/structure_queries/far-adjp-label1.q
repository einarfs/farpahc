copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}ADJP* idoms N-N|NS-N|NPR-N|NPRS-N|PRO-N)

replace_label{1}: NP-SBJ
