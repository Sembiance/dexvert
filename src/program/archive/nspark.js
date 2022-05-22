import {Program} from "../../Program.js";
import {runUtil} from "xutil";
import {dateParse, path} from "std";

export class nspark extends Program
{
	website = "https://github.com/mjwoodcock/nspark";
	package = "app-arch/nspark";
	bin     = "nspark";
	args    = r => ["-x", r.inFile()];
	cwd     = r => r.outDir();
	verify  = (r, dexFile) => dexFile.name!=="settypes";
	
	// nspark doesn't set dates, but knows about them if I do a listing, so this function will do a listing and set proper dates
	post = async r =>
	{
		const currentYear = new Date().getFullYear();
		const {stderr} = await runUtil.run("nspark", ["-l", "-v", r.inFile()], {cwd : r.cwd});
		const fixedOut = stderr.replace(/-{5}[\s -]+-{5}/, "\n");	// for some reason the column underlines are not on their own line, this fixes that
		const fileDates = Object.fromEntries(fixedOut.split("\n").map(line =>
		{
			const parts = (line.match(/^(?<filePath>\S+)\s+(?<fileSize>)\d+\s(?<day>\d\d)-(?<month>...)-(?<year>\d{4})\s(?<time>\S+)\s+.+$/) || {groups : {}}).groups;
			if(!parts.filePath)
				return null;
			
			if((+parts.year)>currentYear)
				return null;
			
			if((+parts.year)<1970)
				parts.year = currentYear.toString();
				
			const month = ({"jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4, "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8, "sep" : 9, "oct" : 10, "nov" : 11, "dec" : 12}[parts.month.toLowerCase()]).toString().padStart(2, "0");
			return [parts.filePath, dateParse(`${parts.day}.${month}.${parts.year} ${parts.time}`, "dd.MM.yyyy HH:mm:ss")];
		}).filter(v => !!v));
		
		for(const outputFile of r.f.files.new || [])
		{
			const relPath = path.relative(r.outDir({absolute : true}), outputFile.absolute);
			if(!Object.hasOwn(fileDates, relPath))
			{
				r.xlog.warn`Failed to find relative file: ${relPath} ${fileDates}`;
				continue;
			}

			outputFile.setTS(fileDates[relPath].getTime());
		}
	};
	renameOut = false;
}
