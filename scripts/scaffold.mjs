#!/usr/bin/env node
// Node >=18
import { cp, mkdir, readdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const usage = `
Usage:
  node scripts/scaffold.mjs --stack fastify-ts --name my-app [--port 3000] [--out .]
Options:
  --stack   Template folder in scaffold/templates
  --name    New app folder (created under --out)
  --port    Port to inject (default 3000)
  --out     Destination root (default ".")
  --force   Overwrite if target exists
`;

const args = Object.fromEntries(process.argv.slice(2).map((a, i, all) => a.startsWith("--") ? [a.replace(/^--/,""), all[i+1]?.startsWith("--") ? true : all[i+1]] : []));
if (!args.stack || !args.name) {
  console.error(usage);
  process.exit(1);
}

const ROOT = process.cwd();
const SRC = path.join(ROOT, "scaffold", "templates", args.stack);
const OUT_ROOT = path.resolve(ROOT, args.out ?? ".");
const DEST = path.join(OUT_ROOT, args.name);
const tokens = {
  __APP_NAME__: args.name,
  __DESCRIPTION__: `Starter generated from ${args.stack}`,
  __PORT__: String(args.port ?? 3000),
  __YEAR__: String(new Date().getFullYear())
};

// sanity checks
try { await stat(SRC); } catch { console.error(`Template not found: ${SRC}`); process.exit(1); }
try {
  const s = await stat(DEST);
  if (!args.force) { console.error(`Target exists: ${DEST}. Pass --force to overwrite.`); process.exit(1); }
} catch { /* ok, will create */ }

// copy everything first
await mkdir(DEST, { recursive: true });
await cp(SRC, DEST, { recursive: true });

// replace tokens in text files
const TEXT_EXTS = new Set([".md",".json",".ts",".tsx",".js",".jsx",".yml",".yaml",".toml",".env",".gitignore",".dockerignore","",".txt",".cjs",".mjs"]);
async function walkAndReplace(dir) {
  for (const name of await readdir(dir)) {
    const p = path.join(dir, name);
    const st = await stat(p);
    if (st.isDirectory()) { await walkAndReplace(p); continue; }
    const ext = path.extname(name);
    if (!TEXT_EXTS.has(ext) && name !== "Dockerfile") continue;
    let content = await readFile(p, "utf8");
    for (const [k,v] of Object.entries(tokens)) content = content.split(k).join(v);
    // special: set "name" field in package.json if present
    if (name === "package.json") {
      try {
        const pkg = JSON.parse(content);
        pkg.name = args.name;
        content = JSON.stringify(pkg, null, 2) + "\n";
      } catch {/* ignore */}
    }
    await writeFile(p, content, "utf8");
  }
}
await walkAndReplace(DEST);

console.log(`✅ Scaffold created at ${DEST}
Next:
  cd ${args.name}
  npm install
  npm run dev   # or: npm test
`);
