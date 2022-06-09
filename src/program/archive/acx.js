import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil} from "xutil";
import {dateParse} from "std";

export class acx extends Program
{
	website   = "https://github.com/AppleCommander/AppleCommander";
	package   = "app-arch/AppleCommander";
	bin       = "acx";
	args      = r => ["x", "--suggested", "-d", r.inFile(), "-o", r.outDir()];
	renameOut = false;
	chain     = "unHexACX";

	// For 'ProDOS' files (111a_Playboy.dsk), acx/unHexACX doesn't set dates, but acx knows about them if I do a listing, so this function will do a listing and set proper dates
	chainPost = async r =>
	{
		const currentYear = new Date().getFullYear();
		const {stdout} = await runUtil.run("acx", ["ls", "--file", "-d", r.inFile()], {cwd : r.cwd});
		const fileDates = Object.fromEntries(stdout.split("\n").map(line =>
		{
			const parts = (line.match(/^\*?\s+(?<filename>\S+)\s+\S+\s+\S+\s+(?<month>\d+)\/(?<day>\d+)\/(?<year>\d+)\s\d+\/\d+\/\d+\s+.+$/) || {groups : {}}).groups;
			if(!parts.filename)
				return null;
			
			if((+parts.year)>currentYear)
				return null;
			
			if((+parts.year)<1970)
				parts.year = currentYear.toString();
						
			return [parts.filename.toLowerCase(), dateParse(`${parts.day}.${parts.month}.${parts.year} 00:00:00`, "dd.MM.yyyy HH:mm:ss")];
		}).filter(v => !!v));
		
		for(const outputFile of r.f.files.new || [])
		{
			let filename = outputFile.base.toLowerCase();
			if(!Object.hasOwn(fileDates, filename))
				filename = outputFile.name.toLowerCase();

			if(!Object.hasOwn(fileDates, filename))	// we don't log a warning because non-ProDOS disks don't have dates
				continue;

			outputFile.setTS(fileDates[filename].getTime());
		}
	};
}
