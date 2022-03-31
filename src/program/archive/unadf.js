import {Program} from "../../Program.js";
import {runUtil} from "xutil";
import {dateParse, path} from "std";

export class unadf extends Program
{
	website          = "http://lclevy.free.fr/adflib/";
	package          = "app-arch/unadf";
	bin              = "unadf";
	args             = r => [r.inFile(), "-d", r.outDir()];
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	
	// unadf doesn't set dates, but knows about them if I do a listing, so this function will do a listing and set proper dates
	post = async r =>
	{
		const currentYear = new Date().getFullYear();
		const {stdout} = await runUtil.run("unadf", ["-lr", r.inFile()], {cwd : r.cwd});
		const fileDates = Object.fromEntries(stdout.split("\n").map(line =>
		{
			const parts = (line.match(/\s*(?<size>\d*)\s+(?<year>\d{4})\/(?<month>\d\d)\/(?<day>\d\d)\s+(?<hour>\d+):(?<minute>\d+):(?<second>\d+)\s+(?<filePath>.+)/) || {groups : {}}).groups;
			if(!parts.filePath)
				return null;
			
			if((+parts.year)>currentYear)
				return null;
			
			if((+parts.year)<1970)
				parts.year = currentYear.toString();

			if((+parts.hour)>23 || (+parts.minute)>59 || (+parts.second)>59)
				return null;
						
			return [parts.filePath, dateParse(`${parts.day}.${parts.month}.${parts.year} ${parts.hour.padStart(2, "0")}:${parts.minute.padStart(2, "0")}:${parts.second.padStart(2, "0")}`, "dd.MM.yyyy HH:mm:ss")];
		}).filter(v => !!v));
		
		for(const outputFile of r.f.files.new)
		{
			const relPath = path.relative(r.outDir(), outputFile.rel);
			if(!Object.hasOwn(fileDates, relPath))
			{
				r.xlog.warn`Failed to find relative file: ${relPath}`;
				continue;
			}

			outputFile.setTS(fileDates[relPath].getTime());
		}
	};
	renameOut        = false;
}
