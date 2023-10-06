import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, printUtil} from "xutil";

const xlog = new XLog();

// Family durations on ridgeport as of Oct 2023
const familyids =
[
	"text",				//     50s
	"poly",				//     58s
	"font",				//  2m 10s
	"other", 			//  3m  5s
	"executable"		// 10m 38s
];

const reportsDirPath = await fileUtil.genTempPath(undefined, "-testAll");

const startedAt = performance.now();
console.log(printUtil.minorHeader(`Processing ${familyids.length.toLocaleString()} families...`, {prefix : "\n"}));
for(const familyid of familyids)
{
	console.log(printUtil.minorHeader(`Processing ${familyid} family...`, {prefix : "\n"}));
	await runUtil.run("deno", runUtil.denoArgs("testMany.js", `--reportsDirPath=${reportsDirPath}`, `--format=${familyid}`), runUtil.denoRunOpts({liveOutput : true, cwd : xu.dirname(import.meta)}));
}

const elapsed = performance.now()-startedAt;
xlog.info`\nAll Families Elapsed duration: ${fg.peach(elapsed.msAsHumanReadable())}`;
xlog.info`\nReports written to dir: file://${reportsDirPath}`;
