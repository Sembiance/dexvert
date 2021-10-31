import {Program} from "../../Program.js";

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
		r.meta.matches = r.stdout.trim().replaceAll("\n- , ", "\n- ").split("\n- ").filter(v => !!v).map((line, i) => ({magic : line.trim(), from : "file", confidence : 100-i}));
	}
}
