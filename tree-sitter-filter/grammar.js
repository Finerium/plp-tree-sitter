export default grammar({
  name: 'filter',
  extras: $ => [/\s/],
  word: $ => $.identifier,
  rules: {
    query: $ => $._expr,
    _expr: $ => choice($.comparison, $.in_expression, $.contains_expression, $.and_expression, $.or_expression, $.not_expression, $.parenthesized),
    comparison: $ => seq(
      field('field', $.identifier),
      field('operator', choice('=', '!=', '>', '<', '>=', '<=')),
      field('value', $._value),
    ),
    // status in ("open", "pending")
    in_expression: $ => seq(
      field('field', $.identifier),
      'in',
      '(', field('value', $._value), repeat(seq(',', field('value', $._value))), ')',
    ),
    // title contains "invoice", pencarian teks jadi nilainya hanya string
    contains_expression: $ => seq(
      field('field', $.identifier),
      'contains',
      field('value', $.string),
    ),
    and_expression: $ => prec.left(2, seq(field('left', $._expr), 'and', field('right', $._expr))),
    or_expression: $ => prec.left(1, seq(field('left', $._expr), 'or', field('right', $._expr))),
    not_expression: $ => prec(3, seq('not', field('operand', $._expr))),
    parenthesized: $ => seq('(', $._expr, ')'),
    _value: $ => choice($.string, $.number, $.boolean),
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    string: $ => /"[^"]*"/,
    number: $ => /\d+(\.\d+)?/,
    boolean: $ => choice('true', 'false'),
  }
});
