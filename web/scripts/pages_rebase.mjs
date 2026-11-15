// Prefix root-absolute public asset paths in dist/ with the GitHub Pages base (e.g. /endulus/).
import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const base = process.argv[2] || "/endulus/";
const re = /(["'`])\/(data|figures|earth_atlas|moon_atlas|thumbs)\//g;

function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (/\.(js|json|html)$/.test(name)) {
      const src = readFileSync(p, "utf8");
      const out = src.replace(re, `$1${base}$2/`);
      if (out !== src) writeFileSync(p, out);
    }
  }
}
walk(fileURLToPath(new URL("../dist", import.meta.url)));
console.log(`rebased dist assets to ${base}`);
