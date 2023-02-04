import {Program} from "../../Program.js";

export class dskconv extends Program
{
	website      = "http://www.seasip.info/Unix/LibDsk/";
	package      = "app-emulation/libdsk";
	checkForDups = true;
	unsafe       = true;
	bin          = "dskconv";
	args         = async r => [r.inFile(), "-otype", "raw", await r.outFile("out.img")];
	renameOut    = true;
	chain        = "dexvert[asFormat:archive/rawPartition]";
	verify       = (r, dexFile) => dexFile.size<Math.max(r.f.input.size*3);	// some files are mistakenly identified as things like copyQMDiskImage and huge files are created
}
