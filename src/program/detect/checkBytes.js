import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class checkBytes extends Program
{
	website = "https://github.com/Sembiance/dexvert/tree/master/bin/checkBytes";
	bin     = Program.binPath("checkBytes/checkBytes");
	loc     = "local";
	args    = r => [r.inFile()];
	post    = r =>
	{
		r.meta.detections = r.stdout.trim().split("\n").filter(v => !!v).map(line => Detection.create({value : line.trim(), from : "checkBytes", file : r.f.input}));
	};
}
