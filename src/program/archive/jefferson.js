import {Program} from "../../Program.js";

export class jefferson extends Program
{
	website   = "https://github.com/onekey-sec/jefferson/";
	package   = "sys-fs/jefferson";
	bin       = "jefferson";
	args      = r => [r.inFile(), "--force", "--dest", r.outDir()];
	renameOut = false;
}
