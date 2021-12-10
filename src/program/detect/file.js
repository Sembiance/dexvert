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
		r.meta.detections = r.stdout.trim().replaceAll("\n- , ", "\n- ").split("\n- ").filter(v => !!v).map((line, i) => Detection.create({value : line.trim(), from : "file", confidence : 100-i, file : r.f.input}));
	};
	renameOut = false;
}
