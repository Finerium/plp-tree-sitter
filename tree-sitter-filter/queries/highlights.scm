["and" "or" "not" "in" "contains"] @keyword
["=" "!=" ">" "<" ">=" "<="] @operator
["(" ")"] @punctuation.bracket
"," @punctuation.delimiter
(string) @string
(number) @number
(boolean) @constant.builtin
; nama field ada di tiga jenis node, bukan cuma comparison
(comparison field: (identifier) @property)
(in_expression field: (identifier) @property)
(contains_expression field: (identifier) @property)
