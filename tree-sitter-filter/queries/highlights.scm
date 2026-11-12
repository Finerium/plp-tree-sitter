["and" "or" "not"] @keyword
["=" "!=" ">" "<" ">=" "<="] @operator
(string) @string
(number) @number
(boolean) @constant.builtin
(comparison field: (identifier) @property)
