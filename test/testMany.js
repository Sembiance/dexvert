import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";
import {formats, init as initFormats} from "../src/format/formats.js";
import {mkWeblink} from "./testUtil.js";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test multiple formats, creating a report for each",
	opts    :
	{
		reportsDirPath : {desc : "Which directory to write the reports. Default: random"},
		format         : {desc : "Specify one or more formats. Can specify 'all' or an entire family with just image or partials like image/a", required : true, hasValue : true, multiple : true}
	}});

await initFormats(xlog);

const formatsToProcess = new Set();
for(const format of Object.values(formats))
{
	if(format.unsupported)
		continue;

	const formatid = `${format.family.familyid}/${format.formatid}`;
	if(argv.format[0]==="all" || argv.format.some(v => formatid.startsWith(v)))
		formatsToProcess.add(formatid);
}

let formatCount = 0;
const reports = {};
const startedAt = performance.now();
const maxFormatidLength = Array.from(formatsToProcess, v => v.length).max();
const failures = [];
const MAX_LINE_LENGTH = Deno.hostname()==="crystalsummit" ? 118 : 145;
const SLOW_FORMATS_AT_ONCE = 2;
const FORMATS_AT_ONCE = 4;

// these formats are slow, they run first, ordered slowest to fastest (the number is how many minutes that format took to test), but only at max SLOW_FORMATS_AT ONCE in order to ensure we fully utilize all our various bottlenecks in dexvert
const SLOW_FORMATS =
{
	// archive
	"archive/innoSetupInstaller"         : 11,
	"archive/installShieldSelfExtractor" : 6,
	"archive/iso"                        : 9,
	"archive/macromediaDirector"         : 69,
	"archive/swf"                        : 6,
	
	// audio
	"audio/aviAudio"            : 4,
	"audio/fmodSampleBank"      : 16,
	"audio/proPinballSoundbank" : 5,
	"audio/quickTimeAudio"      : 10,
	"audio/soundFont2"          : 7,

	// document
	"document/amigaGuide"            : 7,
	"document/hlp"                   : 4,
	"document/hyperWriter"           : 5,
	"document/multimediaViewerBook"  : 3,
	"document/pageMaker"             : 4,
	"document/palmPeanutReaderEBook" : 2,
	"document/quarkXPress"           : 4,

	// executable
	"executable/dll" : 1,
	"executable/exe" : 2,

	// font
	"font/amigaBitmapFont"        : 1,
	"font/amigaBitmapFontContent" : 1,
	"font/gemFont"                : 1,

	// image
	"image/elecbyteMUGENSprites" : 10,
	"image/micrografxDraw"       : 8,
	"image/trs"                  : 9,
	"image/wgtSprite"            : 5,
	"image/xRes"                 : 5,

	// music
	"music/ay"                 : 9,
	"music/ayAMAD"             : 3,
	"music/chaosMusicComposer" : 5,
	"music/fuxoftAYLanguage"   : 4,
	
	// other
	"other/frameMakerHelp" : 1,
	"other/javaClass"      : 4,
	"other/pogNames"       : 1,

	// poly
	"poly/dxf"                   : 18,
	"poly/rayDreamDesignerScene" : 8,
	"poly/softimageXSI"          : 8,

	// text
	"text/linuxLiveCDInfo"  : 2,
	"text/linuxMakeConfig"  : 1,
	"text/sonnetProject"    : 4,
	"text/txt"              : 3,
	"text/tornado3DProject" : 2,

	// video
	"video/avi"          : 6,
	"video/mov"          : 6,
	"video/trilobyteVDX" : 5,
	"video/vivo"         : 5,
	"video/wmv"          : 11
};

console.log(printUtil.minorHeader(`Processing ${formatsToProcess.size.toLocaleString()} formats...`, {prefix : "\n"}));

const formatsRemaining = Array.from(formatsToProcess).shuffle();
const slowFormatsRemaining = formatsRemaining.filter(formatid => Object.hasOwn(SLOW_FORMATS, formatid)).sortMulti([formatid => SLOW_FORMATS[formatid] || 0], [true]);
formatsRemaining.filterInPlace(formatid => !slowFormatsRemaining.includes(formatid));

const underway = new Set();
const underwaySlow = new Set();

await [].pushSequence(1, formatsRemaining.length+slowFormatsRemaining.length).parallelMap(async () =>
{
	let formatid;
	if(underwaySlow.size<SLOW_FORMATS_AT_ONCE && slowFormatsRemaining.length)
	{
		formatid = slowFormatsRemaining.shift();
		underwaySlow.add(formatid);
	}
	else
	{
		formatid = formatsRemaining.pop() || slowFormatsRemaining.shift();
	}

	underway.add(formatid);
	const formatStartedAt = performance.now();
	const {stdout} = await runUtil.run("deno", runUtil.denoArgs("testdexvert.js", `--format=${formatid}`, "--json"), runUtil.denoRunOpts({cwd : import.meta.dirname}));
	const formatElapsed = performance.now()-formatStartedAt;
	const testData = xu.parseJSON(stdout);
	underway.delete(formatid);
	underwaySlow.delete(formatid);

	const line = [];
	line.push(`${fg.peach(formatElapsed.msAsHumanReadable({short : true, maxParts : 2}).padStart(8))}`);
	line.push(` ${fg.orange(formatid.padEnd(maxFormatidLength)).replaceAll("/", `${fg.cyan("/")}${xu.c.fg.orange}`)}`);
	line.push(` ${fg.cyan((formatsToProcess.size-(++formatCount)).toLocaleString().padStart(formatsToProcess.size.toLocaleString().length))} remain `);
	line.push(` ${fg.cyan(underway.size.toLocaleString().padStart(formatsToProcess.size.toLocaleString().length))} ${xu.colon("underway")}`);
	
	const underwayFormatted = (argv.format.length===1 && argv.format[0]!=="all" && !argv.format[0].includes("/")) ? Array.from(underway, o => o.split("/")[1]).join(" ") : Array.from(underway).join(" ");
	line.push(fg.green(underwayFormatted.innerTruncate(MAX_LINE_LENGTH-line.join("").decolor().length)).replaceAll("…", `${fg.cyan("…")}${xu.c.fg.green}`));
	console.log(line.join(""));

	if(!testData)
		return failures.push(`${fg.orange(formatid.padStart(maxFormatidLength, " "))} ${fg.red("FAILED")}: ${stdout}`);

	reports[formatid] = testData;
}, FORMATS_AT_ONCE);
const elapsed = performance.now()-startedAt;

if(failures.length)
{
	console.log(printUtil.minorHeader(`${failures.length} ${fg.red("FAILURES!")}`, {prefix : "\n"}));
	for(const failure of failures)
		xlog.info`${failure}`;
}

const reportsDirPath = argv.reportsDirPath || await fileUtil.genTempPath("/mnt/dexvert/test", "-testMany");
await Deno.mkdir(reportsDirPath, {recursive : true});

const families = Object.keys(reports).map(v => v.split("/")[0]).unique().sortMulti();
const testManyReportFilePath = path.join(reportsDirPath, "index.html");

await fileUtil.writeTextFile(testManyReportFilePath, `
<html>
	<head>
		<meta charset="UTF-8">
		<title>testMany Report</title>
		<style>
			body, html
			{
				background-color: #1a1a1a;
				color: #ccc;
				font-family: "Terminus (TTF)";
			}

			a, a:visited
			{
				color: #8585ff;
			}

			th
			{
				text-decoration: underline;
				text-align: center;
				font-size: 1.1em;
			}

			th, td
			{
				padding: 0 0.5em;
			}

			td
			{
				text-align: right;
			}

			td.good
			{
				color: #00ff00;
			}

			td.bad
			{
				color: #ff0000;
			}

			td.red
			{
				color: #ff0000;
			}

			td.orange
			{
				color: #ffa000;
			}

			td.yellow
			{
				color: #ffff00;
			}
		</style>
	</head>
	<body>
		<h2>Total elapsed duration: ${elapsed.msAsHumanReadable()}</h2>
		host: ${Deno.hostname()}<br>
		args: ${argv.format.join(" ")}<hr>
		${families.map(family => `
			<h1>${family}</h1>
			<table>
				<thead>
					<tr>
						<th>formatid</th>
						<th>qty</th>
						<th>pass</th>
						<th>fail</th>
						<th>new</th>
						<th>duration</th>
					</tr>
				</thead>
				<tbody>
					${Object.entries(reports).filter(([formatid]) => formatid.split("/")[0]===family).sortMulti([([, o]) => (+o.failCount)===0, ([, o]) => (+o.newSuccessesCount)===0, ([formatid]) => formatid]).map(([formatid, o]) => `<tr>
						<td style="text-align: left;">${o.reportFilePath ? `<a href="${mkWeblink(o.reportFilePath)}">${formatid.escapeHTML()}</a>` : formatid.escapeHTML()}</td>
						<td class="${o.sampleFileCount===0 ? "bad" : ""}">${o.sampleFileCount.toLocaleString()}</td>
						<td class="${(+o.successPercentage || 0)<10 ? "red" : ((+o.successPercentage || 0) < 40 ? "orange" : ((+o.successPercentage || 0) < 100 ? "yellow" : "good"))}">${o.successPercentage || "0"}%</td>
						<td class="${+o.failCount ? "bad" : "good"}">${o.failCount.toLocaleString()}</td>
						<td class="${+o.newSuccessesCount ? "bad" : "good"}">${(o.newSuccessesCount || 0).toLocaleString()}</td>
						<td>${o.elapsed.msAsHumanReadable()}</td>
					</tr>`).join("")}
				</tbody>
			</table>
		`).join("<br><br><br><hr>")}
	</body>
</html>`);

xlog.info`\nElapsed: ${elapsed.msAsHumanReadable()}`;
xlog.info`Reports written to: ${mkWeblink(testManyReportFilePath)}`;
