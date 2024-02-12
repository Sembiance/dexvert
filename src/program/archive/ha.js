import {xu} from "xu";
import {Program} from "../../Program.js";
import {path, dateParse} from "std";
import {fileUtil} from "xutil";

export class ha extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/HA";
	loc     = "dos";
	bin     = "HA.EXE";
	cwd     = r => r.outDir();
	dosData = r => ({autoExec : [`..\\dos\\HA.EXE lf ${r.inFile({backslash : true})} > DEXVERTL.TXT`, `..\\dos\\HA.EXE xy ${r.inFile({backslash : true})}`], runIn : "out"});

	// HA.EXE doesn't set the date/time for each file, but it does know what they are with a list, so we manually set the date and times ourselves
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
		
		let seenStart = false;
		let seenEnd = false;
		let itemLineNum = null;
		let itemInfo = null;
		const itemInfos = [];
		listContentRaw.split("\n").forEach(line =>
		{
			if(seenEnd)
				return;

			if(line.startsWith("==="))
			{
				if(seenStart)
				{
					seenEnd = true;
				}
				else
				{
					itemLineNum = 0;
					itemInfo = {};
					seenStart = true;
				}

				return;
			}

			if(!seenStart)
				return;
			
			if(line.startsWith("---"))
			{
				itemInfos.push(itemInfo);
				itemLineNum = 0;
				itemInfo = {};
				return;
			}

			if(itemLineNum===null)
				return;
			
			if(itemLineNum===0)
			{
				const lineParts = line.match(/^\s*(?<filename>\S+)\s+(?<osize>\d+)\s+(?<csize>\d+)\s+(?<pct>\S+)\s%\s+(?<date>\S+)\s+(?<time>\S+)\s+.*/)?.groups;
				itemInfo.filename = lineParts.filename;
				itemInfo.ts = dateParse(`${lineParts.date} ${lineParts.time}`, "yyyy-MM-dd HH:mm")?.getTime();
			}
			else if(itemLineNum===1)
			{
				itemInfo.dir = line.match(/^\s*(?<hash>\S+)\s+(?<dir>\S+)\s+/)?.groups?.dir?.trim();
				itemInfo.dir = (itemInfo.dir==="(none)" ? "" : itemInfo.dir.replaceAll("\\", "/"));
			}

			itemLineNum++;
		});

		await itemInfos.parallelMap(async o =>
		{
			const fileOutputPath = fileOutputPaths.find(v => path.relative(r.outDir({absolute : true}), v).toLowerCase()===path.join(o.dir, o.filename));
			if(!fileOutputPath)
			{
				r.xlog.warn`Failed to find output file for HA file ${o}`;
				return;
			}

			await Deno.utime(fileOutputPath, Math.floor(o.ts/xu.SECOND), Math.floor(o.ts/xu.SECOND));
		});
	};
	renameOut = false;
}
