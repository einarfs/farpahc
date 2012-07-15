copy_corpus:t

define: def/verbtopic.def
node: IP*
query: 
({1}C iprecedes VB*) AND (IP* idoms C) AND (IP* idoms VB*) AND (C idoms at*)

replace_label{1}: TO
