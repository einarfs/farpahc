copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}NP* idomsonly P)

replace_label{1}: PP
