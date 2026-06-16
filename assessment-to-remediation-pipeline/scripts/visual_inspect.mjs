#!/usr/bin/env node
import { createRequire } from "node:module";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";

const projectRoot = path.resolve(path.join(import.meta.dirname, ".."));
const publicRoot = path.resolve(path.join(projectRoot, ".."));
const requireFromHere = createRequire(import.meta.url);
const outputDir = path.join(projectRoot, "reports", "visual-inspection");
const screenshotDir = path.join(outputDir, "screenshots");

const cases = [
  {
    label: "student-desktop",
    file: "previews/student_form.html",
    width: 1440,
    height: 1200,
    expectedTitle: "SAT Math Readiness Diagnostic Prototype Student Preview",
    expectedH1: "SAT Math Readiness Diagnostic Prototype",
    expectedMarkers: ["Public-safe student preview", "Module 1", "Module 2"],
  },
  {
    label: "student-mobile",
    file: "previews/student_form.html",
    width: 390,
    height: 900,
    expectedTitle: "SAT Math Readiness Diagnostic Prototype Student Preview",
    expectedH1: "SAT Math Readiness Diagnostic Prototype",
    expectedMarkers: ["Public-safe student preview", "Module 1", "Module 2"],
  },
  {
    label: "instructor-desktop",
    file: "previews/instructor_review.html",
    width: 1440,
    height: 1200,
    expectedTitle: "SAT Math Readiness Diagnostic Prototype Instructor Review",
    expectedH1: "SAT Math Readiness Diagnostic Prototype Instructor Review",
    expectedMarkers: ["Instructor review preview", "Review status", "Answer Feedback"],
  },
  {
    label: "instructor-mobile",
    file: "previews/instructor_review.html",
    width: 390,
    height: 900,
    expectedTitle: "SAT Math Readiness Diagnostic Prototype Instructor Review",
    expectedH1: "SAT Math Readiness Diagnostic Prototype Instructor Review",
    expectedMarkers: ["Instructor review preview", "Review status", "Answer Feedback"],
  },
];

const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
  ".txt": "text/plain; charset=utf-8",
};

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (originalError) {
    const candidates = [
      process.env.PLAYWRIGHT_MODULE_DIR,
      ...(process.env.NODE_PATH ? process.env.NODE_PATH.split(path.delimiter) : []),
      path.join(publicRoot, "grant-mccurdy.github.io", "node_modules", "playwright"),
      path.join(publicRoot, "grant-mccurdy.github.io", "node_modules"),
    ].filter(Boolean);

    for (const candidate of candidates) {
      for (const specifier of [path.join(candidate, "playwright"), candidate]) {
        try {
          return requireFromHere(specifier);
        } catch {
          // Try next candidate.
        }
      }
    }

    throw originalError;
  }
}

function staticServer() {
  return http.createServer((request, response) => {
    const requestUrl = new URL(request.url ?? "/", "http://127.0.0.1");
    const pathname = decodeURIComponent(requestUrl.pathname);
    const relativePath = pathname === "/" ? "previews/student_form.html" : pathname.replace(/^\/+/, "");
    const target = path.resolve(projectRoot, relativePath);

    if (target !== projectRoot && !target.startsWith(projectRoot + path.sep)) {
      response.writeHead(403);
      response.end("Forbidden");
      return;
    }

    let filePath = target;
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      filePath = path.join(filePath, "index.html");
    }

    if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
      response.writeHead(404);
      response.end("Not found");
      return;
    }

    response.writeHead(200, {
      "Content-Type": mimeTypes[path.extname(filePath)] ?? "application/octet-stream",
    });
    fs.createReadStream(filePath).pipe(response);
  });
}

async function listen(server) {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Could not start local visual inspection server");
  }
  return `http://127.0.0.1:${address.port}`;
}

async function closeServer(server) {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

function relative(filePath) {
  return path.relative(projectRoot, filePath).replaceAll(path.sep, "/");
}

async function inspectPage(page, testCase) {
  const bodyText = await page.locator("body").innerText();
  const title = await page.title();
  const h1 = await page.locator("h1").first().innerText();
  const itemCount = await page.locator(".item").count();
  const moduleCount = await page.locator(".module").count();
  const missingMarkers = testCase.expectedMarkers.filter((marker) => !bodyText.includes(marker));
  const overflow = await page.evaluate(() =>
    Array.from(document.querySelectorAll("body *"))
      .filter((el) => {
        const rect = el.getBoundingClientRect();
        return (
          rect.width &&
          rect.height &&
          (rect.right > document.documentElement.clientWidth + 2 || rect.left < -2)
        );
      })
      .slice(0, 8)
      .map((el) => ({
        tag: el.tagName,
        className: String(el.className),
        text: (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 90),
      })),
  );

  const failures = [];
  if (title !== testCase.expectedTitle) failures.push(`unexpected title: ${title}`);
  if (h1 !== testCase.expectedH1) failures.push(`unexpected h1: ${h1}`);
  if (itemCount !== 36) failures.push(`expected 36 items, found ${itemCount}`);
  if (moduleCount !== 2) failures.push(`expected 2 modules, found ${moduleCount}`);
  if (bodyText.length < 1000) failures.push("body text is unexpectedly short");
  if (missingMarkers.length) failures.push(`missing markers: ${missingMarkers.join(", ")}`);
  if (overflow.length) failures.push(`horizontal overflow detected in ${overflow.length} element(s)`);

  return {
    label: testCase.label,
    file: testCase.file,
    viewport: { width: testCase.width, height: testCase.height },
    title,
    h1,
    itemCount,
    moduleCount,
    bodyTextLength: bodyText.length,
    missingMarkers,
    overflow,
    failures,
  };
}

function renderMarkdown(results) {
  const failures = results.filter((result) => result.failures.length);
  const rows = results
    .map(
      (result) =>
        `| ${result.label} | ${result.viewport.width}x${result.viewport.height} | ${result.itemCount} | ${result.moduleCount} | ${result.failures.length ? "FAIL" : "PASS"} |`,
    )
    .join("\n");
  const details = results
    .map((result) => {
      const screenshot = `reports/visual-inspection/screenshots/${result.label}.png`;
      const failureText = result.failures.map((item) => `- ${item}`).join("\n") || "- None";
      return `### ${result.label}

- file: \`${result.file}\`
- screenshot: \`${screenshot}\`
- title: \`${result.title}\`
- h1: \`${result.h1}\`
- body text length: \`${result.bodyTextLength}\`

Failures:

${failureText}
`;
    })
    .join("\n");

  return `# Visual Inspection

Status: \`${failures.length ? "FAIL" : "PASS"}\`

This report was generated from local static previews. It opened no external sites, used no credentials, made no Canvas calls, and submitted nothing.

| Case | Viewport | Items | Modules | Status |
| --- | ---: | ---: | ---: | --- |
${rows}

## Case Details

${details}

## Automated Review Boundary

This inspection is advisory. It does not approve assessment items, create Canvas quizzes, or replace structured GPT-5.5 item review.
`;
}

fs.mkdirSync(screenshotDir, { recursive: true });

const { chromium } = await loadPlaywright();
const server = staticServer();
const baseUrl = await listen(server);
const browser = await chromium.launch({ headless: true });
const results = [];

try {
  for (const testCase of cases) {
    const page = await browser.newPage({ viewport: { width: testCase.width, height: testCase.height } });
    await page.goto(`${baseUrl}/${testCase.file}`, { waitUntil: "networkidle" });
    const screenshotPath = path.join(screenshotDir, `${testCase.label}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const result = await inspectPage(page, testCase);
    result.screenshot = relative(screenshotPath);
    results.push(result);
    await page.close();
  }
} finally {
  await browser.close();
  await closeServer(server);
}

const report = {
  generated_at: "not_recorded_for_reproducible_offline_review",
  mode: "local_static_preview",
  safety_boundary: "no external sites, credentials, Canvas calls, uploads, sends, or submissions",
  cases: results,
  status: results.some((result) => result.failures.length) ? "FAIL" : "PASS",
};

fs.writeFileSync(path.join(outputDir, "visual-inspection.json"), `${JSON.stringify(report, null, 2)}\n`);
fs.writeFileSync(path.join(outputDir, "visual-inspection.md"), renderMarkdown(results));
console.log(JSON.stringify(report, null, 2));

if (report.status !== "PASS") {
  process.exitCode = 1;
}
