import {xu} from "xu";
import {Program, CONVERT_PNG_ARGS} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

export class chsetKB extends Program
{
	website   = "https://github.com/xiphoseer/sdo-tool";
	package   = "app-text/sdo-tool";
	bin       = "chset-kb";
	args      = r => [r.inFile(), r.outDir()];
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		
		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		if(fileOutputPaths.length!==2)
			return;

		const outPNGFilePath = await r.outFile("out.png", {absolute : true});
		await runUtil.run("magick", [...fileOutputPaths.sortMulti(), "+append", ...CONVERT_PNG_ARGS, outPNGFilePath], {timeout : xu.MINUTE});
		if(await fileUtil.exists(outPNGFilePath))
		{
			await fileUtil.unlink(fileOutputPaths[0]);
			await fileUtil.unlink(fileOutputPaths[1]);
		}
	};
	renameOut = true;
}
