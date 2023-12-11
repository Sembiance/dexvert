import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class checkBytes extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	package = "app-arch/checkBytes";
	bin     = "checkBytes";
	loc     = "local";
	args    = r => [r.inFile()];
	post    = r =>
	{
		r.meta.detections = r.stdout.trim().split("\n").filter(v => !!v).map(line => Detection.create({value : line.trim(), from : "checkBytes", file : r.f.input}));
	};
	renameOut = false;
}
