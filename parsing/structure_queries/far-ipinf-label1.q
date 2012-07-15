copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}IP-INF* idomsonly N-G|NS-G|NPR-G|NPRS-G|PRO-G|Q*-G)

replace_label{1}: NP-POS
