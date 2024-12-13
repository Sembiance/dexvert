import {Program} from "../../Program.js";

export class unsquashfs extends Program
{
	website   = "https://github.com/plougher/squashfs-tools/";
	package   = "sys-fs/squashfs-tools";
	bin       = "unsquashfs";
	args      = r => ["-quiet", "-no-progress", "-ignore-errors", "-dest", r.outDir(), r.inFile()];
	renameOut = false;
}
