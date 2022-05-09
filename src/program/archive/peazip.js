import {xu} from "xu";
import {Program} from "../../Program.js";

export class peazip extends Program
{
	website    = "https://github.com/peazip/PeaZip";
	package    = "app-arch/peazip";
	bin        = "peazip";
	runOptions = ({virtualX : true, timeout : xu.SECOND*30, killChildren : true});	// timeout is because there is no way to bypass password prompts
	args       = r => ["-ext2simplei", r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut  = false;
}
