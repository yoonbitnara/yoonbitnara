const fs = require('fs');
const path = require('path');
const Parser = require('rss-parser');

function parseArgs() {
  var rssUrl = process.argv[2] || '';
  var count = parseInt(process.argv[3] || '5', 10);
  var dateFormat = process.argv[4] || 'yyyy-mm-dd';

  if (!rssUrl) {
    console.error('RSS URL이 필요합니다.');
    process.exit(1);
  }
  if (isNaN(count) || count < 1) {
    count = 5;
  }
  return { rssUrl: rssUrl, count: count, dateFormat: dateFormat };
}

function formatDate(d, fmt) {
  if (!d || fmt === 'none') return '';
  var date = new Date(d);
  var y = String(date.getFullYear());
  var m = String(date.getMonth() + 1).padStart(2, '0');
  var day = String(date.getDate()).padStart(2, '0');
  return fmt === 'yyyy.mm.dd' ? y + '.' + m + '.' + day : y + '-' + m + '-' + day;
}

function buildListMarkdown(items, dateFormat) {
  var lines = [];
  for (var i = 0; i < items.length; i++) {
    var it = items[i];
    var title = it.title || '(제목 없음)';
    var dateStr = formatDate(it.isoDate || it.pubDate, dateFormat);
    lines.push('[' + dateStr + '] ' + title.replace(/\n/g, ' ').trim());
  }
  if (lines.length === 0) {
    lines.push('[----] 최근 글을 찾지 못했습니다.');
  }
  return lines.join('\n');
}

function replaceBetweenMarkers(content, newBlock) {
  var start = '<!-- BLOG-POST-LIST:START -->';
  var end = '<!-- BLOG-POST-LIST:END -->';
  var pattern = new RegExp(start + '[\\s\\S]*?' + end, 'm');
  var replacement = start + '\n' + newBlock + '\n' + end;
  if (!pattern.test(content)) {
    console.error('README에 마커가 없습니다.');
    process.exit(1);
  }
  return content.replace(pattern, replacement);
}

async function main() {
  var args = parseArgs();
  var parser = new Parser();
  var feed = await parser.parseURL(args.rssUrl);
  var items = Array.isArray(feed.items) ? feed.items.slice(0, args.count) : [];
  var listMd = buildListMarkdown(items, args.dateFormat);

  var readmePath = path.join(process.cwd(), 'README.md');
  var readme = fs.readFileSync(readmePath, 'utf8');
  var updated = replaceBetweenMarkers(readme, listMd);

  if (updated !== readme) {
    fs.writeFileSync(readmePath, updated, 'utf8');
    console.log('README 갱신 완료 (' + items.length + '개 항목).');
  } else {
    console.log('변경 사항 없음.');
  }
}

main().catch(function (err) {
  console.error(err);
  process.exit(1);
});

