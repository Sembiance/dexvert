import {Program} from "../../Program.js";

export class hfsexplorer extends Program
{
	website    = "https://github.com/unsound/hfsexplorer";
	bin        = Program.binPath("hfsexplorer/dist/bin/unhfs");
	flags   = {
		partition : "Which partition to extract. Default: 0"
	};
	args       = r => ["-o",  r.outDir({absolute : true}), "-partition", (r.flags.partition || 0).toString(), r.inFile({absolute : true})];
	runOptions = ({cwd : Program.binPath("hfsexplorer/dist")});
	renameOut  = false;
}
