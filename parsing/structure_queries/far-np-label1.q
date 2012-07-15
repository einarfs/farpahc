copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
(PP* idoms {1}NP-*)

replace_label{1}: NP
