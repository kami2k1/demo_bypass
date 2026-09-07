(() => {
  "use strict";

  const GO_KEYWORDS = new Set([
    "break", "case", "chan", "const", "continue", "default", "defer", "else",
    "fallthrough", "for", "func", "go", "goto", "if", "import", "interface",
    "map", "package", "range", "return", "select", "struct", "switch", "type",
    "var",
  ]);

  const GO_TYPES = new Set([
    "any", "bool", "byte", "comparable", "complex64", "complex128", "error",
    "float32", "float64", "int", "int8", "int16", "int32", "int64", "rune",
    "string", "uint", "uint8", "uint16", "uint32", "uint64", "uintptr",
    "true", "false", "nil", "iota", "append", "cap", "close", "copy", "delete",
    "len", "make", "max", "min", "new", "panic", "print", "recover",
  ]);

  const TOKEN = new RegExp(
    [
      "(//[^\\n]*|/\\*[\\s\\S]*?\\*/|#[^\\n]*)",
      "(\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'|`[^`]*`)",
      "\\b(0[xX][0-9a-fA-F_]+|\\d[\\d_]*(?:\\.\\d+)?(?:[eE][+-]?\\d+)?)\\b",
      "([A-Za-z_][A-Za-z0-9_]*)",
    ].join("|"),
    "g",
  );

  const escapeHtml = (text) =>
    text.replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[ch]);

  const wrap = (cls, text) => `<span class="${cls}">${escapeHtml(text)}</span>`;

  function highlight(source) {
    let out = "";
    let last = 0;

    for (const match of source.matchAll(TOKEN)) {
      const [raw, comment, str, number, word] = match;
      out += escapeHtml(source.slice(last, match.index));
      last = match.index + raw.length;

      if (comment) {
        out += wrap("tok-comment", raw);
      } else if (str) {
        out += wrap("tok-string", raw);
      } else if (number) {
        out += wrap("tok-number", raw);
      } else if (GO_KEYWORDS.has(word)) {
        out += wrap("tok-keyword", raw);
      } else if (GO_TYPES.has(word)) {
        out += wrap("tok-type", raw);
      } else if (source[last] === "(") {
        out += wrap("tok-func", raw);
      } else {
        out += escapeHtml(raw);
      }
    }
    return out + escapeHtml(source.slice(last));
  }

  function paintCodeBlocks() {
    for (const block of document.querySelectorAll("pre.code > code")) {
      block.innerHTML = highlight(block.textContent);
    }
  }

  function enableCopyButtons() {
    for (const button of document.querySelectorAll("[data-copy]")) {
      button.addEventListener("click", async () => {
        const figure = button.closest(".code-figure");
        const code = figure?.querySelector("pre.code > code");
        if (!code) return;

        try {
          await navigator.clipboard.writeText(code.textContent);
          button.textContent = "Đã copy";
          button.dataset.copied = "true";
          setTimeout(() => {
            button.textContent = "Copy";
            delete button.dataset.copied;
          }, 1600);
        } catch {
          button.textContent = "Không copy được";
        }
      });
    }
  }

  function closeNavOnNavigate() {
    const toggle = document.getElementById("nav-toggle");
    if (!toggle) return;
    document
      .querySelectorAll(".nav a")
      .forEach((link) => link.addEventListener("click", () => (toggle.checked = false)));
  }

  paintCodeBlocks();
  enableCopyButtons();
  closeNavOnNavigate();
})();
