const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const BASE_DIR = path.dirname(__dirname);
const JSON_PATH = path.join(BASE_DIR, 'report', 'analysis_results.json');
const OUTPUT_PATH = path.join(BASE_DIR, 'report', 'EDA_Report.pptx');

// Load Data
const data = JSON.parse(fs.readFileSync(JSON_PATH, 'utf-8'));

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Antigravity';
pres.title = 'Saramin Marketer EDA Report';

// Bento Grid Colors
const COLORS = {
  bg: "F8F8F2",
  navy: "1A1A2E",
  yellow: "E8FF3B",
  coral: "FF6B6B",
  teal: "4ECDC4",
  warm: "FFE66D",
  white: "FFFFFF",
  gray: "888888"
};

// Common slide background
pres.defineSlideMaster({
  title: 'BENTO_MASTER',
  background: { color: COLORS.bg }
});

// Helper: draw Bento cell
function drawCell(slide, x, y, w, h, bgColor, title, contentLines, value = "", isDark = false) {
  // Box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: w, h: h,
    fill: { color: bgColor },
    line: { color: "DDDDDD", width: 1 }
  });
  
  const textColor = isDark ? COLORS.white : COLORS.navy;
  const labelColor = isDark ? COLORS.yellow : COLORS.gray;

  // Title
  slide.addText(title, {
    x: x + 0.2, y: y + 0.2, w: w - 0.4, h: 0.3,
    fontSize: 14, bold: true, color: labelColor, margin: 0, fontFace: "Helvetica"
  });

  // Large Value
  if (value) {
    slide.addText(value, {
      x: x + 0.2, y: y + 0.5, w: w - 0.4, h: 1.0,
      fontSize: 44, bold: true, color: textColor, margin: 0, fontFace: "Helvetica"
    });
  }

  // Content
  const contentY = value ? y + 1.5 : y + 0.6;
  if (contentLines && contentLines.length > 0) {
    const textOpts = {
      x: x + 0.2, y: contentY, w: w - 0.4, h: h - (contentY - y) - 0.2,
      fontSize: 12, color: textColor, margin: 0, fontFace: "Helvetica", valign: "top"
    };
    
    // Convert to bullet objects
    const bullets = contentLines.map(line => ({ text: line, options: { breakLine: true, bullet: true } }));
    slide.addText(bullets, textOpts);
  }
}

// SLIDE 1: Title
let slide1 = pres.addSlide({ masterName: "BENTO_MASTER" });
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1.5, w: 8, h: 2.5,
  fill: { color: COLORS.navy }
});
slide1.addText("데이터로 보는 마케터 채용 시장", {
  x: 1.5, y: 1.8, w: 7, h: 1,
  fontSize: 36, bold: true, color: COLORS.yellow, fontFace: "Helvetica"
});
slide1.addText("사람인 데이터 기반 핵심 직무 역량 분석 리포트", {
  x: 1.5, y: 2.8, w: 7, h: 0.5,
  fontSize: 18, color: COLORS.white, fontFace: "Helvetica"
});

// SLIDE 2: Market Overview
let slide2 = pres.addSlide({ masterName: "BENTO_MASTER" });
slide2.addText("시장 요약 (Market Overview)", { x: 0.5, y: 0.3, fontSize: 24, bold: true, color: COLORS.navy });

// Total jobs
drawCell(slide2, 0.5, 1.0, 3, 4, COLORS.navy, "분석 공고 수", [], String(data.summary.total_jobs), true);

// Locations
const locs = Object.entries(data.summary.top_locations).map(e => `${e[0]} (${e[1]}건)`);
drawCell(slide2, 3.8, 1.0, 5.7, 1.8, COLORS.white, "주요 근무 지역", locs);

// Experience
const exps = Object.entries(data.summary.top_experience).map(e => `${e[0]} (${e[1]}건)`);
drawCell(slide2, 3.8, 3.1, 5.7, 1.9, COLORS.white, "요구 경력 분포", exps);


// SLIDE 3: Job Categories
let slide3 = pres.addSlide({ masterName: "BENTO_MASTER" });
slide3.addText("직무군 분포 (Job Categories)", { x: 0.5, y: 0.3, fontSize: 24, bold: true, color: COLORS.navy });

let catY = 1.0;
const catEntries = Object.entries(data.categories);
// top 2 categories
drawCell(slide3, 0.5, 1.0, 4.3, 4, COLORS.teal, "가장 수요가 높은 직무군", [
  `1위: ${catEntries[0][0]} (${catEntries[0][1]}건)`,
  `2위: ${catEntries[1][0]} (${catEntries[1][1]}건)`,
  "트렌드: 퍼포먼스와 IT/콘텐츠에 집중된 수요."
], "", false);

const otherCats = catEntries.slice(2, 5).map(e => `${e[0]}: ${e[1]}건`);
drawCell(slide3, 5.1, 1.0, 4.4, 4, COLORS.white, "기타 유관 직무군", otherCats);


// SLIDE 4: TF-IDF Keywords
let slide4 = pres.addSlide({ masterName: "BENTO_MASTER" });
slide4.addText("핵심 역량 키워드 (TF-IDF)", { x: 0.5, y: 0.3, fontSize: 24, bold: true, color: COLORS.navy });

const reqKws = data.keywords.required.slice(0, 7).map(k => `${k.word} (${k.score})`);
drawCell(slide4, 0.5, 1.0, 4.3, 4, COLORS.coral, "필수 자격 요건 (Required)", reqKws, "", false);

const prefKws = data.keywords.preferred.slice(0, 7).map(k => `${k.word} (${k.score})`);
drawCell(slide4, 5.1, 1.0, 4.4, 4, COLORS.warm, "우대 사항 (Preferred)", prefKws, "", false);


// SLIDE 5: Strategy
let slide5 = pres.addSlide({ masterName: "BENTO_MASTER" });
slide5.addText("구직 전략 (Actionable Insights)", { x: 0.5, y: 0.3, fontSize: 24, bold: true, color: COLORS.navy });

drawCell(slide5, 0.5, 1.0, 9, 4, COLORS.navy, "💡 인사이트 요약", data.insights, "", true);


pres.writeFile({ fileName: OUTPUT_PATH }).then(() => {
    console.log(`PPTX created at ${OUTPUT_PATH}`);
});
