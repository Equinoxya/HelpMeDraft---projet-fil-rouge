import { marked } from "marked";
import createDOMPurify from "dompurify";
import { JSDOM } from "jsdom";
const DOMPurify = createDOMPurify(new JSDOM("").window);

const markedOptions = { gfm: true, breaks: true, headerIds: false, mangle: false };
const cases = [
  '<img src=x onerror="alert(1)">',
  '<script>alert(1)</script>',
  '<a href="javascript:alert(1)">clic</a>',
  '<iframe src="https://evil.tld"></iframe>',
  '<svg/onload=alert(1)>',
  '# Titre\n\n**gras** *ital* <u>souligné</u>\n\n- a\n- b\n\n[lien](https://exemple.fr)\n\n`code`',
];
for (const md of cases) {
  const raw = marked.parse(md, markedOptions);
  const clean = DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
  console.log("--- entrée :", JSON.stringify(md.slice(0, 48)));
  console.log("    AVANT  :", raw.trim().replace(/\n/g, " "));
  console.log("    APRÈS  :", clean.trim().replace(/\n/g, " "));
}
