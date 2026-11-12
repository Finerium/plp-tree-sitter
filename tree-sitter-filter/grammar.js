/**
 * @file DSL filter untuk kotak pencarian halaman admin (Tugas 4 PLP)
 * @author Ghaisan Khoirul Badruzaman
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

export default grammar({
  name: "filter",

  rules: {
    // TODO: add the actual grammar rules
    source_file: $ => "hello"
  }
});
