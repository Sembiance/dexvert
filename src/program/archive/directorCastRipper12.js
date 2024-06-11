import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class directorCastRipper12 extends Program
{
	website   = "https://github.com/n0samu/DirectorCastRipper";
	loc       = "wine";
	bin       = "DirectorCastRipper_D12/DirectorCastRipper.exe";
	exclusive = "wine";
	args      = r => ["--cli", "--formats", "png", "--formats", "rtf", "--files", `c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`, "--output-folder", `c:\\out${r.wineCounter}`, "--include-names"];
	wineData  = {
		script : `
		Func DismissWarnings()
			;WindowDismiss("[TITLE:Error]", "", "{ENTER}")
			WindowDismiss("Locate replacement", "", "{ESCAPE}")
			WindowDismiss("Where is", "", "{ESCAPE}")
			WindowDismiss("Director Player Error", "", "{ENTER}")
			;WindowDismiss("Missing Fonts", "", "{ENTER}")
			return Not ProcessExists("DirectorCastRipper.exe")
		EndFunc
		CallUntil("DismissWarnings", ${xu.MINUTE*6})`,	// some samples like pok18pc.dir have a TON of dialogs to dismiss and didn't finish in under 2 minutes, so we bump to 6
		timeout : xu.MINUTE*6
	};
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const relFilePaths = await fileUtil.tree(outDirPath, {relative : true, nodir : true});
		
		// These 3 CSV files are output even for protected files. So if that's all we have, we delete them which marks this as having failed which then allows other techniques to work (impulse.dir for example needs to be decompiled first)
		if(relFilePaths.filter(relFilePath => !["Casts.csv", "Members.csv", "Movies.csv"].includes(path.basename(relFilePath))).length===0)
		{
			r.xlog.info`No real files found`;
			await relFilePaths.parallelMap(async relFilePath => await fileUtil.unlink(path.join(outDirPath, relFilePath)));
			return;
		}

		// colapse all files into a single directory and ensure files that start with ###_ are at least 5 digits long with leading 0s
		await relFilePaths.parallelMap(async relFilePath =>
		{
			if(!relFilePath.includes("/"))
				return;

			await Deno.rename(path.join(outDirPath, relFilePath), path.join(outDirPath, path.basename(relFilePath).replace(/^\d+/, v => v.padStart(5, "0"))));
		});
	};
	verify = async (r, dexFile) =>	// eslint-disable-line require-await
	{
		// If the Casts.csv file is exactly 33 bytes, it's an empty dummy file that DirectorCastRipper creates and isn't useful to keep
		if(dexFile.base==="Casts.csv" && dexFile.size===33)
			return false;

		if(dexFile.base==="Export.log")
			return false;

		return true;
	};
	renameOut = false;
}
