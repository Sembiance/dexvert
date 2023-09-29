import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";
import {formats, init as initFormats} from "../src/format/formats.js";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test multiple formats, creating a report for each",
	opts    :
	{
		format : {desc : "Specify one or more formats", hasValue : true, multiple : true},
		family : {desc : "Specifcy one or more families", hasValue : true, multiple : true}
	}});

const formatsToProcess = new Set(argv.format || []);

if(argv.family?.length)
{
	await initFormats(xlog);
	for(const familyid of argv.family)
	{
		for(const format of Object.values(formats))
		{
			if(format.simple || format.unsupported)
				continue;

			if(format.family.familyid===familyid)
				formatsToProcess.add(`${familyid}/${format.formatid}`);
		}
	}
}

const reports = {};
await Array.from(formatsToProcess).parallelMap(async formatid =>
{
	xlog.info`Doing format: ${formatid}`;

	const {stdout} = await runUtil.run("deno", runUtil.denoArgs("testdexvert.js", `--format=${formatid}`, "--report", "--json"), runUtil.denoRunOpts({cwd : xu.dirname(import.meta)}));
	reports[formatid] = xu.parseJSON(stdout);
});

const testManReportFilePath = path.join("/mnt/ram/tmp/testMany.html");
await fileUtil.writeTextFile(testManReportFilePath, `
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
		</style>
	</head>
	<body>
		<table>
			<thead>
				<tr>
					<th>formatid</th>
					<th>qty</th>
					<th>pass</th>
					<th>fail</th>
					<th>duration</th>
				</tr>
			</thead>
			<tbody>
				${Object.entries(reports).map(([formatid, o]) => `<tr>
					<td><a href="${o.reportFilePath}">${formatid.escapeHTML()}</a></td>
					<td>${o.sampleFileCount.toLocaleString()}</td>
					<td class="${+o.failCount ? "bad" : "good"}">${o.successPercentage}%</td>
					<td class="${+o.failCount ? "bad" : "good"}">${o.failCount.toLocaleString()}</td>
					<td>${o.elapsed.msAsHumanReadable()}</td>
				</tr>`).join("")}
			</tbody>
		</table>
	</body>
</html>`);
xlog.info`\nReport written to: file://${testManReportFilePath}`;
