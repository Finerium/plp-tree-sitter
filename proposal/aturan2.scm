; aturan 2: argumen pertama berupa penggabungan string dengan +
(call_expression
  function: (member_expression property: (property_identifier) @method)
  arguments: (arguments . (binary_expression operator: "+") @sql)
  (#match? @method "^(query|execute|raw)$"))
