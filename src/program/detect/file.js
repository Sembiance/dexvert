import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class file extends Program
{
	website = "https://www.darwinsys.com/file/";
	package = "sys-apps/file";
	bin     = "file";
	loc     = "local";
	args    = r => ["--dereference", "--brief", "--keep-going", "--raw", r.inFile()];
	post    = r =>
	{
		const fileMatches = [];
		let fileMatch = null;
		for(let line of r.stdout.trim().split("\n"))
		{
			line = line.replace(/^- /g, "").trim();
			line = line.replace(/^FILE_SIZE=\d+/, "").trim();
			if(!line.length)
				continue;

			if(!fileMatch)
			{
				fileMatch = line;
				continue;
			}
			
			if([", ", "], ", "), ", "(", "; "].some(v => line.startsWith(v)) || fileMatch.trim().endsWith("["))
			{
				fileMatch += line;
				continue;
			}

			fileMatches.push(fileMatch);
			fileMatch = line;
		}

		fileMatches.push(fileMatch);
		r.meta.detections = fileMatches.filter(v => !!v).map((v, i) => Detection.create({value : v.trim(), from : "file", confidence : 100-i, file : r.f.input}));
	};
	renameOut = false;
}
