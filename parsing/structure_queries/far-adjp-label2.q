copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}ADJP* idoms N-A|NS-A|NPR-A|NPRS-A|PRO-A)

replace_label{1}: NP-OB1
