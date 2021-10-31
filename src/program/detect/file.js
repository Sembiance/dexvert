import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class file extends Program
{
	website        = "https://www.darwinsys.com/file/";
	gentooPackage  = "sys-apps/file";
	gentooUseFlags = "bzip2 lzma seccomp zlib";

	bin = "file";
	loc = "local";

	args = r => ["--dereference", "--brief", "--keep-going", "--raw", r.input.primary.rel]
	post = r =>
	{
		r.meta.detections = r.stdout.trim().replaceAll("\n- , ", "\n- ").split("\n- ").filter(v => !!v).map((line, i) => Detection.create({value : line.trim(), from : "file", confidence : 100-i, file : r.inputOriginal.primary}));
	}
}
