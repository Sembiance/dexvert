import {xu} from "xu";
import {XLog} from "xlog";
import { fileUtil, printUtil} from "xutil";
import {path} from "std";

const xlog = new XLog("info", {noANSI : true});

const OUT_FILE_PATH = "/tmp/out.txt";
if(!await fileUtil.exists(OUT_FILE_PATH))
	Deno.exit(xlog.error`File not found: ${OUT_FILE_PATH}`);

const allowedRanges = [
	
	[0x0000, 0x007F],  // Basic Latin (English)
	[0x0080, 0x00FF],  // Latin-1 Supplement (includes many special characters used in Mac systems)
	[0x0100, 0x017F],  // Latin Extended-A (includes characters like ƒ)
	[0x0180, 0x024F],  // Latin Extended-B
	[0x2100, 0x214F],  // Letterlike Symbols (includes ™ trademark symbol)
	[0x2190, 0x21FF],  // Arrows (includes ↵ carriage return symbol)
	[0x4E00, 0x9FFF],  // CJK Unified Ideographs (Common Kanji)
	[0x3400, 0x4DBF],  // CJK Unified Ideographs Extension A (Less common Kanji)
	[0x3040, 0x309F],  // Hiragana
	[0x30A0, 0x30FF],  // Katakana
	[0x3000, 0x303F],  // CJK Symbols and Punctuation
	[0x31F0, 0x31FF],  // Katakana Phonetic Extensions
	[0xF900, 0xFAFF],  // CJK Compatibility Ideographs
	[0xFF00, 0xFFEF],  // Half-width and Full-width Forms
	[0x2500, 0x25FF],  // Box Drawing (includes □ white square symbol)
	[0xE000, 0xF8FF],  // Private Use Area (contains various vendor-specific characters)
	[0x2600, 0x26FF],  // Miscellaneous Symbols (includes ★ black star symbol)
	[0x2000, 0x206F]   // General Punctuation
];

function isCodePointAllowed(codePoint)
{
	return allowedRanges.some(([start, end]) => codePoint >= start && codePoint <= end);
}

function containsOnlyEnglishAndJapanese(v)
{
	for(const char of v)
	{
		const codePoint = char.codePointAt(0);
		if(!isCodePointAllowed(codePoint))
			return {char, codePoint};
	}
}

const ignoreLines =
[
	"Aladdin",
	"DropStuff",
	"Eudora",
	"StuffIt",
	"ShrinkWrap"
];

const invalids =
{
	filenames : [],
	fullPaths : []
};

let lastItemid = null;
for(const line of (await fileUtil.readTextFile(OUT_FILE_PATH)).decolor().split("\n"))
{
	// if line starts with a number check with regex
	let {itemid, text} = line.match(/^\s*(?<itemid>\d+)\t(?<text>.+)$/)?.groups || {};
	if(itemid)
		lastItemid = +itemid;
	else
		itemid = lastItemid;
	text ||= line;

	if(ignoreLines.some(v => text.includes(v)))
		continue;

	const filename = path.basename(text);
	let r = null;
	if(filename!==text)
	{
		r = containsOnlyEnglishAndJapanese(filename);
		if(r)
			invalids.filenames.push({itemid, char : r.char, codePoint : r.codePoint, text});
	}

	if(!r)
	{
		r = containsOnlyEnglishAndJapanese(text);
		if(r)
			invalids.fullPaths.push({itemid, char : r.char, codePoint : r.codePoint, text});
	}
}

console.log(printUtil.columnizeObjects(invalids.filenames, {maxWidth : 80}).decolor());
console.log(printUtil.columnizeObjects(invalids.fullPaths, {maxWidth : 80}).decolor());

const invaliditemids = [...invalids.filenames.map(o => +o.itemid), ...invalids.fullPaths.map(o => +o.itemid)].unique().sortMulti();
console.log(invaliditemids.join(" "));
xlog.info`filenames: ${invalids.filenames.length}\nfullPaths: ${invalids.fullPaths.length}\nitemids: ${invaliditemids.length}`;
