import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, printUtil} from "xutil";

const xlog = new XLog();

// Family durations on ridgeport as of Oct 2023
const familyids =
[
	"executable",		//     29s
	"poly",				//     37s
	"text",				//     57s
	"font",				//  1m  4s
	"other", 			//  1m 42s
	"video", 			//  9m 11s
	"audio", 			// 10m 25s
	"music", 			// 12m 28s
	"document",			// 17m 23s
	"image",			// 20m 51s
	"archive"			// 
];

const reportsDirPath = await fileUtil.genTempPath(undefined, "-testAll");

const startedAt = performance.now();
console.log(printUtil.minorHeader(`Processing ${familyids.length.toLocaleString()} families...`, {prefix : "\n"}));
while(familyids.length)
{
	
}


for(const familyid of familyids)
{
	console.log(printUtil.minorHeader(`Processing ${familyid} family...`, {prefix : "\n"}));
	await runUtil.run("deno", runUtil.denoArgs("testMany.js", `--reportsDirPath=${reportsDirPath}`, `--format=${familyid}`), runUtil.denoRunOpts({liveOutput : true, cwd : xu.dirname(import.meta)}));
}

const elapsed = performance.now()-startedAt;
xlog.info`\nAll Families Elapsed duration: ${fg.peach(elapsed.msAsHumanReadable())}`;
xlog.info`\nReports written to dir: file://${reportsDirPath}`;
