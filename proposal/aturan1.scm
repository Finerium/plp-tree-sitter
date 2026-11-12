; aturan 1: argumen pertama .query/.execute/.raw berupa template string yang punya ${...}
(call_expression
  function: (member_expression property: (property_identifier) @method)
  arguments: (arguments . (template_string (template_substitution)) @sql)
  (#match? @method "^(query|execute|raw)$"))
