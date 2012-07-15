copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}VBPS|VBDS idoms *i-*) AND (VBPS|VBDS idoms !veri-*)

replace_label{1}: VBPI
