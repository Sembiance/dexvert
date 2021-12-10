import {xu} from "xu";
import {Program} from "../../Program.js";
import {path, dateParse} from "std";
import {fileUtil} from "xutil";

export class swagv extends Program
{
	website  = "http://fileformats.archiveteam.org/wiki/SWG";
	unsafe   = true;
	loc      = "dos";
	bin      = "SWAG/SWAGV.EXE";
	args     = r => ["/V", `..\\..\\${r.inFile()}`, ">", "..\\..\\OUT\\DEXVERTL.TXT"];
	dosData  = ({runIn : "prog"});
	postExec = async r =>
	{
		const listFilePath = path.join(r.f.root, "out", "DEXVERTL.TXT");
		if(!(await fileUtil.exists(listFilePath)))
		{
			r.xlog.warn`Failed to find DEXVERTL.TXT from SWAGV.EXE execution: ${listFilePath}`;
			return;
		}

		const listContentRaw = new TextDecoder("latin1").decode(await Deno.readFile(listFilePath));

		const pasFiles = [];
		for(const line of listContentRaw.split("\n"))
		{
			// Num  Length   Size  %   Date    Time  CRC  Attr Subject
			//----- ------  ----- --- -------  ----- ---- ---- -----------------------------
			//(  1)  37638  10462 73% 05-28-93 13:45 7349 ---w General PASCAL FAQ
			const lineParts = (line.trim().match(/\(\s*(?<num>\d+)\)\s+(?<len>\d+)\s+(?<size>\d+)\s+(?<pct>\d+)%\s+(?<ts>\d+-\d+-\d+)\s+(?<tsTime>\d+:\d+)\s+(?<crc>\S+)\s+(?<attr>\S+)\s+(?<desc>.+)/) || {groups : null}).groups;
			if(!lineParts)
				continue;
			
			const tsParts = lineParts.ts.split("-");
			tsParts.splice(2, 1, `${(+tsParts.at(-1))<20 ? "20" : "19"}${tsParts.at(-1)}`);
			const tsPart = tsParts.join("-");
			pasFiles.push({num : lineParts.num, filename : `${lineParts.num.toString().padStart(4, "0")}_${lineParts.desc.replaceAll("/", "-")}.pas`, ts : dateParse(tsPart, "MM-dd-yyyy")?.getTime()||0});
		}

		r.meta.pasFiles = pasFiles;

		await fileUtil.unlink(listFilePath);
	};
	renameOut = false;
}
