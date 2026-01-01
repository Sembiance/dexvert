import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class diskExpressInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	loc     = "dos";
	flags   = {
		outDirname : "Dirname where the DEXVERTL.TXT file should be output, overrides default"
	};
	pre      = async r => await fileUtil.writeTextFile(path.join(r.cwd, "DOSEXE.bat"), ["@ECHO OFF", `${r.inFile()} /d > ..\\${r.flags.outDirname || r.f.outDir.base}\\DEXVERTI.TXT`, "EXIT"].join("\n"));
	bin      = "DOSEXE.bat";
	dosData  = () => ({runIn : "absolute", timeout : xu.SECOND*30});
	postExec = async r =>
	{
		const infoFilePath = path.join(r.f.root, r.flags.outDirname || r.f.outDir.base, "DEXVERTI.TXT");
		if(!await fileUtil.exists(infoFilePath))
		{
			r.xlog.warn`Failed to find DEXVERTI.TXT from diskExpressInfo program: ${infoFilePath}`;
			return;
		}

		for(const line of (await fileUtil.readTextFile(infoFilePath)).split("\n"))
		{
			const {size} = line.match((/(?<size>[\d.]+[KM]) diskette image/))?.groups || {};
			if(size)
				r.meta.size = size;
		}

		if(r.meta.size)
			r.meta.bytes = {"160K" : 163_840, "180K" : 184_320, "320K" : 327_680, "360K" : 368_640, "720K" : 737_280, "1.2M" : 1_228_800, "1.44M" : 1_474_560, "2.88M" : 2_949_120}[r.meta.size];

		await fileUtil.unlink(infoFilePath);
	};
	renameOut = false;
}
