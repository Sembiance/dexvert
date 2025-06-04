import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {getWineDriveC} from "../../wineUtil.js";

const _TEMP_DIR_PREFIXES = ["TEMP", "users/sembiance/Temp", "windows/temp"];
const _TRANSLATE_PREFIXES =
{
	"users/sembiance/Temp/" : "",	// this is where InstallShield Self-Extractors tend to extract into, so just remove this prefix for cleaner output
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
		
		r.createdFilePaths = new Set();
		const copyingFiles = new Set();
		const waitingToCopy = new Set();
		const outDirPath = path.join(r.outDir({absolute : true}));
		// the first thing these programs seem to do is extract the files. After that they attempt to install silently, but this almost always fails. Some like HWSETUP.EXE delete their temp files when they fail
		// so we set up a file monitor to auto-copy any created files to the output directory. It's a bit hacky, but it seems to work
		r.monitorO = await fileUtil.monitor(r.wineTreeRootDirPath, async ({filePath, type}) =>
		{
			if(type==="ready" || !filePath)
				return;

			const relFilePath = path.relative(r.wineTreeRootDirPath, filePath);
			if((/^in\d+\//).test(relFilePath))
				return;

			if(type==="create")
				r.createdFilePaths.add(relFilePath);

			if(!["create", "modify"].includes(type) || !r.createdFilePaths.has(relFilePath))
				return;

			if(waitingToCopy.has(relFilePath))
				return;

			if(copyingFiles.has(relFilePath))
			{
				waitingToCopy.set(relFilePath);
				await xu.waitUntil(() => !copyingFiles.has(relFilePath));
				copyingFiles.add(relFilePath);
				waitingToCopy.delete(relFilePath);
			}

			copyingFiles.add(relFilePath);
			const outFilePath = path.join(outDirPath, _translatePrefix(relFilePath));
			await Deno.mkdir(path.dirname(outFilePath), {recursive : true});
			await xu.tryFallbackAsync(async () => await Deno.copyFile(filePath, outFilePath));
			copyingFiles.delete(relFilePath);
		});
	};
	postExec = async r =>
	{
		if(r.monitorO?.stop)
			await r.monitorO.stop();

		const outDirPath = r.outDir({absolute : true});
		for(const newFilePath of Array.from(r.createdFilePaths))
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
