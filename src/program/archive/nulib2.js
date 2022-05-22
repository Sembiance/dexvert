import {Program} from "../../Program.js";
import {runUtil} from "xutil";
import {dateParse} from "std";

export class nulib2 extends Program
{
	website          = "https://github.com/fadden/nulib2";
	package          = "app-arch/nulib2";
	bin              = "nulib2";
	args             = r => ["-x", r.inFile()];
	cwd              = r => r.outDir();
	
	// nulib2 doesn't set dates, but knows about them if I do a listing, so this function will do a listing and set proper dates
	post = async r =>
	{
		const currentYear = new Date().getFullYear();
		const {stdout} = await runUtil.run("nulib2", ["-v", r.inFile()], {cwd : r.cwd});
		const fileDates = Object.fromEntries(stdout.split("\n").map(line =>
		{
			const {filename, monthStr, day, year, hour, minute} = line.match(/.(?<filename>\S+)\s+\S+\s+\S+\s+(?<day>\d+)-(?<monthStr>[^-]+)-(?<year>\d+)\s(?<hour>\d+):(?<minute>\d+)\s+\S+\s+(?<fileSize>\d+)$/)?.groups || {};
			if(!filename)
				return null;
			
			const fullYear = (+year)<70 ? 2000+(+year) : 1900+(+year);
			if(fullYear>currentYear)
				return null;

			if((+hour)>23 || (+minute)>59)
				return null;
			
			const month = [null, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].indexOf(monthStr);
			return [filename, dateParse(`${day.padStart(2, "0")}.${month.toString().padStart(2, "0")}.${fullYear} ${hour.padStart(2, "0")}:${minute.padStart(2, "0")}:00`, "dd.MM.yyyy HH:mm:ss")];
		}).filter(v => !!v));
		
		for(const outputFile of r.f.files.new || [])
		{
			if(!Object.hasOwn(fileDates, outputFile.base))
			{
				r.xlog.warn`Failed to find file: ${outputFile}`;
				continue;
			}

			outputFile.setTS(fileDates[outputFile.base].getTime());
		}
	};
	renameOut = false;
}
