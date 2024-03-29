import {xu} from "xu";
import {Program} from "../../Program.js";
import {path, dateParse} from "std";
import {fileUtil} from "xutil";

export class lhark extends Program
{
	website = "https://www.sac.sk/download/pack/lhark04d.zip";
	loc     = "dos";
	bin     = "LHARK.EXE";
	cwd     = r => r.outDir();
	dosData = r => ({autoExec : [`..\\dos\\LHARK.EXE l ${r.inFile({backslash : true})} > DEXVERTL.TXT`, `..\\dos\\LHARK.EXE e ${r.inFile({backslash : true})}`], runIn : "out"});

	// LHARK.EXE doesn't set the date/time for each file, but it does know what they are with a list, so we manually set the date and times ourselves
	postExec = async r =>
	{
		const listFilePath = path.join(r.outDir({absolute : true}), "DEXVERTL.TXT");
		if(!await fileUtil.exists(listFilePath))
			return;
		
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true});
		if(fileOutputPaths.length===0 || (fileOutputPaths.length===1 && fileOutputPaths.includes(listFilePath)))
		{
			await fileUtil.unlink(listFilePath);
			return;
		}

		const listContentRaw = await fileUtil.readTextFile(listFilePath);
		await fileUtil.unlink(listFilePath);
		await listContentRaw.split("\n").parallelMap(async line =>
		{
			const o = line.trim().match(/^.{4}\s(?<year>\d\d)-(?<month>\d\d)-(?<day>\d\d)\s(?<time>\d\d:\d\d)\s\S+\s+\d+\s\S+\s+\d+\s\S+\s(?<filename>.+)$/)?.groups;
			if(!o)
				return;

			const fileOutputPath = fileOutputPaths.find(v => path.basename(v).toLowerCase()===o.filename.toLowerCase());
			if(!fileOutputPath)
				return r.xlog.warn`Failed to find output file for LHARK file ${o}`;

			const ts = dateParse(`19${o.year}-${o.month}-${o.day} ${o.time}`, "yyyy-MM-dd HH:mm")?.getTime();
			await Deno.utime(fileOutputPath, Math.floor(ts/xu.SECOND), Math.floor(ts/xu.SECOND));
		});
	};
	renameOut = false;
}
