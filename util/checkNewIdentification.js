import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, printUtil} from "xutil";
import {Program} from "../src/Program.js";
import {FileSet} from "../src/FileSet.js";
import {init as initPrograms} from "../src/program/programs.js";

const xlog = new XLog("info");
await initPrograms(xlog);

xlog.info`Finding sample files...`;
const familyid = "document";
const SAMPLES_DIR = `/mnt/compendium/DevLab/dexvert/test/sample/${familyid}`;
const sampleFilePaths = await fileUtil.tree(SAMPLES_DIR, {nodir : true, depth : 2, relative : true});
const bar = printUtil.progress({max : sampleFilePaths.length});
const matches = [];
await sampleFilePaths.parallelMap(async sampleFilePath =>
{
	const formatid = sampleFilePath.split("/")[0];

	const r = await Program.runProgram("identify", await FileSet.create(SAMPLES_DIR, "input", sampleFilePath), {xlog : new XLog("error")});
	bar.increment();
	if(!r?.meta?.detections?.length)
		return;

	matches.push({familyid, formatid, sampleFilePath, value : r.meta.detections[0].value});
}, 10);

for(const match of matches.sortMulti([o => o.familyid, o => o.formatid, o => o.sampleFilePath]))
	xlog.info`${match.familyid}/${match.formatid} ${match.sampleFilePath.padStart(20, " ").innerTruncate(20)}: ${match.value}`;
