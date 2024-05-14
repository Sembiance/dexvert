import {xu} from "xu";
import {fileUtil, printUtil} from "xutil";
import {xmlParse} from "denoLandX";
import {XLog} from "xlog";
import {path} from "std";

const xlog = new XLog();

const triddefsTOC = {};

xlog.info`Finding and loading triddefs...`;
const tridDefsBasePath = "/mnt/compendium/DevLab/dexvert/sandbox/triddefs/defs";
const tridDefFilePaths = await fileUtil.tree(tridDefsBasePath, {regex : /\.xml$/, nodir : true, relative : true});
xlog.info`Loading ${tridDefFilePaths.length.toLocaleString()} triddefs...`;
const progress = printUtil.progress({max : tridDefFilePaths.length});
await tridDefFilePaths.parallelMap(async tridDefFilePath =>
{
	try
	{
		triddefsTOC[xmlParse(await fileUtil.readTextFile(path.join(tridDefsBasePath, tridDefFilePath))).TrID.Info.FileType] = tridDefFilePath;
	}
	catch(err)
	{
		xlog.info`Failed to parse triddef: ${tridDefFilePath}: ${err.toString()}`;
	}

	progress.tick();
});

xlog.info`\nFinished loading triddefs. Saving TOC...`;
await fileUtil.writeTextFile("/mnt/compendium/DevLab/dexvert/sandbox/triddefs/triddefsTOC.json", JSON.stringify(triddefsTOC));

