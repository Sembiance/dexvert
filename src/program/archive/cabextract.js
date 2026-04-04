import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
export class cabextract extends Program
{
	website  = "https://www.cabextract.org.uk/";
	package  = "app-arch/cabextract";
	flags   = {
		winCEInstall : "If this is set, the extracted files will be treated as a WinCE Install package"
	};
	bin      = "cabextract";
	args     = r => ["--directory", r.outDir(), "--fix", r.inFile()];
	postExec = async r =>
	{
		if(!r.flags.winCEInstall)
			return;

		const winCEFilePaths = await fileUtil.tree(r.outDir({absolute : true}), {regex : /\.000$/, depth : 1, nodir : true});
		r.xlog.info`zzzzz: ${winCEFilePaths}`;
		if(winCEFilePaths.length!==1)
			return;

		await runUtil.run("python3", [Program.binPath("wince_000_transform.py"), winCEFilePaths[0]]);
	};
	renameOut = false;
}
