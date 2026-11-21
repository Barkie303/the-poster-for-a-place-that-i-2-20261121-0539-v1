// TIDEFALL — a travel poster for a place that isn't there.
// The poster is drawn by render.py and shipped as entry.png; this
// entrypoint copies it to the output directory, byte for byte,
// so every run of the program hands in the same poster.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const here = dirname(fileURLToPath(import.meta.url));
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
