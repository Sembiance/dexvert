import {xu} from "xu";
import {path} from "std";
import {cmdUtil, fileUtil} from "xutil";
import {DEXRPC_HOST, DEXRPC_PORT} from "../server/dexrpc.js";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	cmdid   : "dexall",
	version : "1.0.0",
	desc    : "Dexverts one or more files",
	opts    :
	{
		outputDir : {desc : "Output directory. Default: Random Directory", hasValue : true, defaultValue : await fileUtil.genTempPath()}
	},
	args :
	[
		{argid : "inputFiles", desc : "Which files to convert", required : true, multiple : true}
	]});

const outputDirPath = path.resolve(path.relative(Deno.cwd(), argv.outputDir));
await fileUtil.unlink(outputDirPath, {recursive : true});
await Deno.mkdir(outputDirPath, {recursive : true});

const families = [];
const reports = [];
const failures = [];
const startedAt = performance.now();
let completed = 0;
await argv.inputFiles.parallelMap(async inputFile =>
{
	if(!await fileUtil.exists(inputFile) || !(await Deno.stat(inputFile)).isFile)
		return completed++;

	const inputFilePath = path.resolve(path.relative(Deno.cwd(), inputFile));
	const inputFilename = path.basename(inputFilePath);
	const outputSubDirPath = path.join(outputDirPath, inputFilename);
	await Deno.mkdir(outputSubDirPath, {recursive : true});

	const o = {op : "dexvert", inputFilePath, outputDirPath : outputSubDirPath, logLevel : "info", prod : true};
	const {r} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(o)}))?.json()), {});
	completed++;
	if(!r?.json?.phase?.format)
	{
		failures.push(inputFilename);
		return xlog.error`Failed to dexvert ${inputFilePath}`;
	}

	families.pushUnique(r.json.phase.family);

	const formatid = `${r.json.phase.family}/${r.json.phase.format}`;
	r.json.actions = [];
	r.json.actions.push({text : "stash", value : `dexstash --record --delete ${formatid} '${inputFilePath}'`});

	r.json.originalInputFilename = inputFilename;
	if(!r.json.created?.files?.output?.length)
	{
		r.json.outputLink = path.join(".", inputFilename);
		r.json.outputLinkText = `no files created`;
	}
	else if(r.json.created?.files?.output?.length===1)
	{
		r.json.outputLink = path.join(".", inputFilename, r.json.created.files.output[0].rel);
		r.json.outputLinkText = r.json.created.files.output[0].base;
	}
	else
	{
		r.json.outputLink = path.join(".", inputFilename);
		r.json.outputLinkText = `${r.json.created.files.output.length.toLocaleString()} files`;
	}

	reports.push(r.json);

	xlog.info`${completed.toLocaleString().padStart(argv.inputFiles.length.toLocaleString().length)} files completed    ${(argv.inputFiles.length-completed).toLocaleString().padStart(argv.inputFiles.length.toLocaleString().length)} remain`;
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
		</style>
	</head>
	<body>
		<input type="text" id="copyTextInput">
		<h2>Total elapsed duration: ${elapsed.msAsHumanReadable()}</h2><hr>
		${failures.length>0 ? `<h3 style="color: red;">Failures (${failures.length.toLocaleString()})</h3>${failures.sortMulti().map(failure => `<span>${failure}</span><br>`).join("")}<br><hr>` : ""}
		${families.map(family => `
			<h1>${family}</h1>
			<table>
				<thead>
					<tr>
						<th>formatid</th>
						<th>duration</th>
						<th>input</th>
						<th>output</th>
						<th>actions</th>
					</tr>
				</thead>
				<tbody>
					${reports.filter(o => o.phase.family===family).sortMulti([o => `${o.phase.family}/${o.phase.format}`]).map(o => `<tr>
						<td>${o.phase.family}/${o.phase.format}</td>
						<td style="text-align: right;">${o.duration.msAsHumanReadable()}</td>
						<td>${o.originalInputFilename}</td>
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
