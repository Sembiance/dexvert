import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class idarc extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/IDArc";
	bin     = Program.binPath("idarc");
	loc     = "local";
	args    = r => [r.flags.detectTmpFilePath];
	post    = r =>
	{
		r.meta.detections = r.stdout.trim().split("\n").filter(v => !!v).map(line => Detection.create({value : `idarc: ${line.trim()}`, from : "idarc", file : r.f.input}));
	};
	renameOut = false;
}
