import {xu} from "xu";
import {path} from "std";
import {cmdUtil, fileUtil, hashUtil} from "xutil";
import {C} from "../C.js";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	cmdid   : "dexall",
	version : "1.0.0",
	desc    : "Dexverts one or more files",
	opts    :
	{
		outputDir : {desc : "Output directory. Default: Random Directory", hasValue : true, defaultValue : await fileUtil.genTempPath()},
		relative  : {desc : "On the report, show the paths as relative to the current working directory"}
	},
	args :
	[
		{argid : "inputFiles", desc : "Which files or directories to convert", multiple : true, required : true}
	]});

let inputFiles = [];
for(const inputFile of (argv.inputFiles || []))
{
	if(!await fileUtil.exists(inputFile))
	{
		xlog.error`Input file/dir does not exist: ${inputFile}`;
		continue;
	}

	if((await Deno.stat(inputFile)).isDirectory)
		inputFiles = inputFiles.concat(await fileUtil.tree(inputFile, {nodir : true}));
	else
		inputFiles.push(inputFile);
}
inputFiles = inputFiles.unique();

const outputDirPath = path.resolve(path.relative(Deno.cwd(), argv.outputDir));
await fileUtil.unlink(outputDirPath, {recursive : true});
await Deno.mkdir(outputDirPath, {recursive : true});

const families = [];
const reports = [];
const failures = [];
const startedAt = performance.now();
let completed = 0;
const existingSums = {};
const allNonNew = [];
await inputFiles.parallelMap(async inputFile =>
{
	if(!await fileUtil.exists(inputFile) || !(await Deno.stat(inputFile)).isFile)
		return completed++;

	const inputFilePath = path.resolve(path.relative(Deno.cwd(), inputFile));
	const inputFilename = path.basename(inputFilePath);
	const outputSubDirPath = path.join(outputDirPath, inputFilename);
	await Deno.mkdir(outputSubDirPath, {recursive : true});

	const o = {op : "dexvert", inputFilePath, outputDirPath : outputSubDirPath};
	const {r} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${C.DEXRPC_HOST}:${C.DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
	completed++;
	if(!r?.json?.processed || !r?.json?.phase?.format)
	{
		failures.push({inputFilePath, ids : r.json.ids || []});
		return xlog.error`Failed to dexvert ${inputFilePath} (${(inputFiles.length-completed).toLocaleString()} remain)`;
	}

	families.pushUnique(r.json.phase.family);

	const formatid = `${r.json.phase.family}/${r.json.phase.format}`;
	if(!existingSums[formatid])
	{
		const existingSampleFilePaths = await fileUtil.tree(path.join(import.meta.dirname, "..", "..", "test", "sample", r.json.phase.family, r.json.phase.format), {nodir : true, depth : 1});
		existingSums[formatid] = await existingSampleFilePaths.parallelMap(async existingSampleFilePath => await hashUtil.hashFile("blake3", existingSampleFilePath));
	}

	const sum = await hashUtil.hashFile("blake3", inputFilePath);
	if(!existingSums[formatid].includes(sum))
		r.json.newFile = true;
	else
		allNonNew.push(inputFilePath);

	r.json.actions = [];
	r.json.actions.push({text : "stash", value : `dexstash ${formatid} '${inputFilePath.replaceAll("'", "'\\''")}'`});
	r.json.actions.push({text : "stash+rm", value : `dexstash --delete ${formatid} '${inputFilePath.replaceAll("'", "'\\''")}'`});
	r.json.actions.push({text : "delete", value : `rm -f '${inputFilePath}'`});

	r.json.originalInputFilename = argv.relative ? path.relative(Deno.cwd(), inputFile) : inputFilename;
	if(!r.json.created?.files?.output?.length)
	{
		r.json.outputLink = path.join(".", inputFilename);
		r.json.outputLinkText = `no files created`;
	}
	else if(r.json.created.files.output.length===1)
	{
		r.json.outputLink = path.join(".", inputFilename, r.json.created.files.output[0]);
		r.json.outputLinkText = path.basename(r.json.created.files.output[0]);
	}
	else
	{
		r.json.outputLink = path.join(".", inputFilename);
		r.json.outputLinkText = `${r.json.created.files.output.length.toLocaleString()} files`;
	}

	reports.push(r.json);

	xlog.info`${completed.toLocaleString().padStart(inputFiles.length.toLocaleString().length)} files completed    ${(inputFiles.length-completed).toLocaleString().padStart(inputFiles.length.toLocaleString().length)} remain`;
}, Math.floor(navigator.hardwareConcurrency*0.90));
const elapsed = performance.now()-startedAt;

const reportFilePath = path.join(outputDirPath, "report.html");
await fileUtil.writeTextFile(reportFilePath, `
<html>
	<head>
		<meta charset="UTF-8">
		<title>dexall Report</title>
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
				text-align: left;
			}

			span[data-copy]
			{
				color: #5382da;
				text-decoration: underline;
				cursor: pointer;
			}

			#copyTextInput
			{
				position: absolute;
				bottom: 0;
				right: 0;
				color: rgba(0,0,0,0);
				background-color: transparent;
				border: 0;
				outline: none;
			}

			tr td:nth-child(6), tr td:nth-child(2)
			{
				white-space: nowrap;
			}

			tr td:nth-child(4)
			{
				color: #00ff00;
			}

			table.failures tbody tr td:nth-child(1)
			{
				vertical-align: top;
			}

			table.failures tbody tr td:nth-child(2)
			{
				padding: 0.5em 0;
			}

			table.failures tbody tr:nth-child(odd)
			{
				background-color: #292929;
			}

			table.failures tr td .weak
			{
				color: rgba(255, 255, 255, 0.1);
			}
		</style>
	</head>
	<body>
		<input type="text" id="copyTextInput">
		<h2>Total elapsed duration: ${elapsed.msAsHumanReadable()}</h2>
		${allNonNew.length ? `<span data-copy="rm -f ${allNonNew.map(v => `'${v.replaceAll("'", "'\\''")}'`).join(" ")}">delete all pre-existing stash files</span>` : ""}<br>
		${failures.length ? `<span data-copy="cp ${failures.map(({inputFilePath}) => `'${inputFilePath.replaceAll("'", "'\\''")}'`).join(" ")} ">copy failures to ...</span>` : ""}<br>
		<hr>
		${failures.length>0 ? `<h3 style="color: red;">Failures (${failures.length.toLocaleString()})</h3>
			<table class="failures">
				<thead>
					<tr>
						<th>filename</th>
						<th>ids</th>
						<th>actions</th>
					</tr>
				</thead>
				<tbody>
					${failures.sortMulti([failure => path.extname(failure.inputFilePath), failure => path.basename(failure.inputFilePath)]).map(failure => `<tr>
						<td>${path.basename(failure.inputFilePath)}</td>
						<td>${failure.ids.map(({from, magic, weak}) => `<span class="${(from==="file" && magic==="data") || (weak) ? "weak" : ""}">${"&nbsp;".repeat(Math.max(0, 10-from.length))}${from}: ${magic}</span>`).join("<br>")}</td>
						<td></td>
					</tr>`).join("")}
				</tbody>
			</table><hr>` : ""}
		${families.map(family => `
			<h1>${family}</h1>
			<table>
				<thead>
					<tr>
						<th>formatid</th>
						<th>duration</th>
						<th>input</th>
						<th>new?</th>
						<th>output</th>
						<th>actions</th>
					</tr>
				</thead>
				<tbody>
					${reports.filter(o => o.phase.family===family).sortMulti([o => !!o.newFile, o => `${o.phase.family}/${o.phase.format}`, o => o.originalInputFilename]).map(o => `<tr>
						<td>${o.phase.family}/${o.phase.format}</td>
						<td style="text-align: right;">${o.duration.msAsHumanReadable({short : true})}</td>
						<td>${o.originalInputFilename}</td>
						<td>${o.newFile ? "new" : ""}</td>
						<td><a href="${o.outputLink.escapeHTML()}">${o.outputLinkText.escapeHTML()}</a></td>
						<td>${o.actions.map(action => `<span data-copy="${action.value.escapeHTML()}">${action.text.escapeHTML()}</span>`).join(" | ")}</td>
					</tr>`).join("")}
				</tbody>
			</table>
		`).join("<br><br><br><hr>")}
		<script>
			document.body.addEventListener("click", evt =>
			{
				if(evt.target.dataset.copy)
				{
					const copyTextInput = document.querySelector("#copyTextInput");
					copyTextInput.value = evt.target.dataset.copy;
					copyTextInput.select();
					document.execCommand("copy");
					copyTextInput.value = "";
					copyTextInput.blur();

					evt.target.closest("tr").style.backgroundColor = "#333";
				}
			});
		</script>
	</body>
</html>`);

xlog.info`\nReport written to: file://${reportFilePath}`;
