import {Program} from "../../Program.js";
import {dateParse} from "std";

export class unlzx extends Program
{
	website = "http://xavprods.free.fr/lzx/";
	package = "app-arch/unlzx";
	flags   = {
		listOnly : "If set to true, only list out the the files in the archive and set meta info, don't actually extract. Default: false"
	};
	bin        = "unlzx";
	args       = r => [r.flags.listOnly ? "-v" : "-x", r.inFile()];
	runOptions = ({stdoutEncoding : "latin1"});
	post       = r =>
	{
		if(!r.flags.listOnly)
			return;
		
		r.meta.fileProps = {};

		r.stdout.trim().split("\n").forEach(line =>
		{
			const parts = (line.match(/^\s*(?<unpackedSize>\d+)\s+(?<packedSize>\d+)\s+(?<tsTime>\S+)\s+(?<tsDate>\S+)\s+(?<attribs>\S+)\s+"(?<filename>.+)"$/) || {groups : {}}).groups;
			if(!parts.tsDate || !parts.tsTime)
				return;
			const dateParts = parts.tsDate.match(/^(?<day>\d+)-(?<month>[^-]+)-(?<year>\d+)$/)?.groups;
			const month = {"jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4, "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8, "sep" : 9, "oct" : 10, "nov" : 11, "dec" : 12}[dateParts.month.toLowerCase()];
			
			const ts = dateParse(`${dateParts.day}-${month}-${dateParts.year} ${parts.tsTime}`, "d-M-yyyy HH:mm:ss");
			r.meta.fileProps[parts.filename] = {unpackedSize : parts.unpackedSize, packedSize : parts.packedSize, ts : ts.getTime(), attribs : parts.attribs};
		});
	};
	renameOut = false;
}
