import {xu} from "xu";
import {XLog} from "xlog";
import {path} from "std";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DEXRPC_HOST, DEXRPC_PORT} from "../src/dexUtil.js";
import {mkWeblink} from "./testUtil.js";
import RandExp from "npm:randexp@0.5.3";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexvert by giving it bad data",
	opts    :
	{
		format : {desc : "Specify one or more formats. Can specify 'all' or an entire family with just image or partials like image/a", required : true, hasValue : true, multiple : true}
	}});

await initFormats(xlog);

const formatsToProcess = [];
for(const format of Object.values(formats))
{
	if(format.unsupported)
		continue;

	const formatid = `${format.family.familyid}/${format.formatid}`;
	if(argv.format[0]==="all" || argv.format.some(v => formatid.startsWith(v)))
		formatsToProcess.push(format.formatid);
}

const DEXFUZZ_ROOT_DIR = await fileUtil.genTempPath("/mnt/dexvert/test", "_fuzz");
const EXTS_SKIP =
[
	// these extensions are well known enough
	".txt",

	// these extensions are distinctive enough
	".amossourcecode",
	".symdef",
	".texi",
	".texinfo"
];

async function fuzzByExt()
{
	const extensionsMap = {};
	for(const formatid of formatsToProcess)
	{
		const format = formats[formatid];
		if(format.forbidExtMatch===true)
			continue;

		const exts = Array.isArray(format.forbidExtMatch) ? format.ext.filter(ext => !format.forbidExtMatch.includes(ext)) : (format.ext || []);
		for(const ext of exts)
		{
			if(EXTS_SKIP.includes(ext))
				continue;
			extensionsMap[ext] ||= [];
			extensionsMap[ext].push(`${format.family.familyid}/${formatid}`);
		}
	}
	const extensions = Object.entries(extensionsMap).map(([ext, sourceFormats]) => ({ext, sourceFormats}));
	if(!extensions.length)
		return;

	const failures = [];
	console.log(printUtil.majorHeader(`Fuzzing ${extensions.length} extensions (from ${formatsToProcess.length} formats)...`, {prefix : "\n"}));
	const bar = printUtil.progress({max : extensions.length, includeDuration : true});
	await extensions.parallelMap(async ({ext, sourceFormats}) =>
	{
		const dirPath = await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR, ext);
		
		const fileSize = Math.randomInt(xu.KB*4, xu.KB*32);
		const inputFilePath = await fileUtil.genTempPath(dirPath, ext);
		const outputDirPath = await fileUtil.genTempPath(dirPath, "out");
		await Deno.mkdir(outputDirPath, {recursive : true});
		await runUtil.run("dd", ["if=/dev/urandom", `of=${inputFilePath}`, `bs=${fileSize}`, "count=1"]);

		const o = {op : "dexvert", inputFilePath, outputDirPath, logLevel : "debug", prod : true, timeout : xu.MINUTE};
		//	o.dexvertOptions.asFormat = diskFormatid;

		const startedAt = performance.now();
		const {r, timedout} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
		if(r?.json?.processed || timedout)
		{
			const logFilePath = await fileUtil.genTempPath(dirPath, ".log.txt");
			await fileUtil.writeTextFile(logFilePath, (r?.pretty || "").decolor());

			const jsonFilePath = await fileUtil.genTempPath(dirPath, ".json");
			await fileUtil.writeTextFile(jsonFilePath, JSON.stringify(r?.json || {}));

			failures.push({sourceFormats, what : ext, fileSize, r, timedout, dirPath, duration : performance.now()-startedAt});
		}
		else
		{
			await fileUtil.unlink(inputFilePath);
			await fileUtil.unlink(outputDirPath, {recursive : true});
		}

		bar.tick();
	});

	await writeReport(await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR, "report.html"), failures);
}

async function fuzzByFileSize()
{
	const fileSizes = [];
	for(const formatid of formatsToProcess)
	{
		const format = formats[formatid];
		if(!format.matchFileSize)
			continue;

		fileSizes.push(...(Array.isArray(format.fileSize) ? format.fileSize : (Object.isObject(format.fileSize) ? Object.values(format.fileSize) : [format.fileSize])).map(fileSize => ({sourceFormats : [`${format.family.familyid}/${formatid}`], fileSize})));
	}
	if(!fileSizes.length)
		return;

	const failures = [];
	console.log(printUtil.majorHeader(`Fuzzing ${fileSizes.length} file sizes (from ${formatsToProcess.length} formats)...`, {prefix : "\n"}));
	
	const bar = printUtil.progress({max : fileSizes.length, includeDuration : true});
	await fileSizes.parallelMap(async ({fileSize, sourceFormats}) =>
	{
		const dirPath = await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR, fileSize.toString());
		
		const inputFilePath = await fileUtil.genTempPath(dirPath, "");
		const outputDirPath = await fileUtil.genTempPath(dirPath, "out");
		await Deno.mkdir(outputDirPath, {recursive : true});
		await runUtil.run("dd", ["if=/dev/urandom", `of=${inputFilePath}`, `bs=${fileSize}`, "count=1"]);

		const o = {op : "dexvert", inputFilePath, outputDirPath, logLevel : "debug", prod : true, timeout : xu.MINUTE};
		//	o.dexvertOptions.asFormat = diskFormatid;

		const startedAt = performance.now();
		const {r, timedout} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
		if(r?.json?.processed || timedout)
		{
			const logFilePath = await fileUtil.genTempPath(dirPath, ".log.txt");
			await fileUtil.writeTextFile(logFilePath, (r?.pretty || "").decolor());

			const jsonFilePath = await fileUtil.genTempPath(dirPath, ".json");
			await fileUtil.writeTextFile(jsonFilePath, JSON.stringify(r?.json || {}));

			failures.push({sourceFormats, what : fileSize, fileSize, r, timedout, dirPath, duration : performance.now()-startedAt});
		}
		else
		{
			await fileUtil.unlink(inputFilePath);
			await fileUtil.unlink(outputDirPath, {recursive : true});
		}

		bar.tick();
	});

	await writeReport(await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR, "report.html"), failures);
}

async function fuzzByFilename()
{
	const filenames = [];
	for(const formatid of formatsToProcess)
	{
		const format = formats[formatid];
		if(!format.filename)
			continue;

		for(const re of format.filename)
		{
			const randExp = new RandExp(re);
			filenames.push({sourceFormats : [`${format.family.familyid}/${formatid}`], filename : randExp.gen()});
		}
	}
	if(!filenames.length)
		return;

	const failures = [];
	console.log(printUtil.majorHeader(`Fuzzing ${filenames.length} filenames (from ${formatsToProcess.length} formats)...`, {prefix : "\n"}));
	
	const bar = printUtil.progress({max : filenames.length, includeDuration : true});
	await filenames.parallelMap(async ({filename, sourceFormats}) =>
	{
		const dirPath = await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR);
		
		const fileSize = Math.randomInt(xu.KB*4, xu.KB*32);
		const inputFilePath = path.join(dirPath, filename);
		const outputDirPath = await fileUtil.genTempPath(dirPath, "out");
		await Deno.mkdir(outputDirPath, {recursive : true});
		await runUtil.run("dd", ["if=/dev/urandom", `of=${inputFilePath}`, `bs=${fileSize}`, "count=1"]);

		const o = {op : "dexvert", inputFilePath, outputDirPath, logLevel : "debug", prod : true, timeout : xu.MINUTE};
		//	o.dexvertOptions.asFormat = diskFormatid;

		const startedAt = performance.now();
		const {r, timedout} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
		if(r?.json?.processed || timedout)
		{
			const logFilePath = await fileUtil.genTempPath(dirPath, ".log.txt");
			await fileUtil.writeTextFile(logFilePath, (r?.pretty || "").decolor());

			const jsonFilePath = await fileUtil.genTempPath(dirPath, ".json");
			await fileUtil.writeTextFile(jsonFilePath, JSON.stringify(r?.json || {}));

			failures.push({sourceFormats, what : filename, fileSize, r, timedout, dirPath, duration : performance.now()-startedAt});
		}
		else
		{
			await fileUtil.unlink(inputFilePath);
			await fileUtil.unlink(outputDirPath, {recursive : true});
		}

		bar.tick();
	});

	await writeReport(await fileUtil.genTempPath(DEXFUZZ_ROOT_DIR, "report.html"), failures);
}
async function writeReport(reportFilePath, failures)
{
	await fileUtil.writeTextFile(reportFilePath, `
<html>
	<head>
		<title>Fuzz: ${Array.force(argv.format || []).map(v => v.escapeHTML())}</title>
		<meta charset="UTF-8">
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

			a
			{
				border: 0;
			}

			thead tr th
			{
				text-decoration: underline;
				text-align: center;
				padding: 0.1em 0.5em;
				color: #eeee00;
			}
						
			thead tr:nth-child(1) th
			{
				font-size: 1.5em;
				text-decoration: none;
				font-weight: bold;
				color: #fff;
				min-width: 10.0em;
			}

			tbody tr:nth-child(even)
			{
				background-color: #292929;
			}
		</style>
	</head>
	<body>
		<table>
			<thead>
				<tr>
					<th colspan="7">${failures.length} Failures</th>
				</tr>
				<tr>
					<th>formats</th>
					<th>what</th>
					<th>file size</th>
					<th>duration</th>
					<th>processed as</th>
					<th>processed with</th>
					<th>dir</th>
				</tr>
			</thead>
			<tbody>
				${failures.sortMulti([o => o.ext]).map(o => `
				<tr>
					<td>${o.sourceFormats.join("<br>")}</td>
					<td>${o.what}</td>
					<td style="text-align: right;">${o.fileSize}</td>
					<td style="text-align: right;">${o.timedout ? "timed out" : o.duration.msAsHumanReadable()}</td>
					<td>${o.r?.json?.phase?.family || ""}/${o.r?.json?.phase?.format || ""}</td>
					<td>${o.r?.json?.phase?.converter}</td>
					<td><a href="${mkWeblink(o.dirPath)}">${path.basename(o.dirPath)}</a></td>
				</tr>`).join("")}
			</tbody>
		</table>
	</body>
</html>`);

	xlog.info`Fuzzing complete. ${failures.length} failures. Report written to ${mkWeblink(reportFilePath)}`;
}

await fuzzByFilename();
await fuzzByFileSize();
await fuzzByExt();
