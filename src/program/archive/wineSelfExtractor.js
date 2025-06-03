import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {getWineDriveC} from "../../wineUtil.js";

const _TEMP_DIR_PREFIXES = ["TEMP", "users/sembiance/Temp", "windows/temp"];
const _TRANSLATE_PREFIXES =
{
	"users/sembiance/Temp/" : "",	// this is where Install Shield Self-Extrators tend to extract into, so just remove this prefix for cleaner output
	"users/sembiance/"      : "users/dexvert/"
};
const _translatePrefix = outFilePathRel =>
{
	for(const [from, to] of Object.entries(_TRANSLATE_PREFIXES))
	{
		if(outFilePathRel.startsWith(from))
		{
			outFilePathRel = to + outFilePathRel.slice(from.length);
			break;
		}
	}
	
	return outFilePathRel;
};

export class wineSelfExtractor extends Program
{
	website  = "https://github.com/Sembiance/dexvert/";
	unsafe   = true;
	loc      = "wine";
	bin      = r => r.inFile({absolute : true});
	args     = () => ["-s"];
	wineData = {
		base    : "base-exclusive",		// due to how this checks before/after execution, need an exclusive base and exclusive runtime lock
		timeout : xu.MINUTE*5			// not all self-extractors will likely honor the '-s' silent flag and do something, they may hang
	};
	exclusive = "base-exclusive";
	pre       = async r =>
	{
		r.wineTreeRootDirPath = getWineDriveC("base-exclusive");
		for(const tempDirPrefix of _TEMP_DIR_PREFIXES)
			await fileUtil.emptyDir(path.join(r.wineTreeRootDirPath, tempDirPrefix));	// in theory this wouldn't be needed because we 'moveFile' below, but if things abort or fail, then previous files don't get cleaned up properly
		r.wineTreeBefore = await fileUtil.tree(r.wineTreeRootDirPath, {nodir : true, relative : true});
		// NOTE: I made a 'fileMonitor' version that is capable of copying temporary files created during the setup execution, but it's not used as it doesn't seem needed. See sandbox/legacy/program/wineSelfExtractor-monitor.js
	};
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		for(const newFilePath of (await fileUtil.tree(r.wineTreeRootDirPath, {nodir : true, relative : true})).subtractAll(r.wineTreeBefore))
		{
			const srcFilePath = path.join(r.wineTreeRootDirPath, newFilePath);
			if(!await fileUtil.exists(srcFilePath))
				continue;

			const outFilePath = path.join(outDirPath, _translatePrefix(newFilePath));

			await Deno.mkdir(path.dirname(outFilePath), {recursive : true});
			await fileUtil.move(srcFilePath, outFilePath);
			await fileUtil.unlink(srcFilePath);
		}
	};

	renameOut = false;
}
