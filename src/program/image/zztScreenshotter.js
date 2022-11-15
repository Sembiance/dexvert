import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("zztScreenshotter");

export class zztScreenshotter extends Program
{
	website    = "https://github.com/Sembiance/dexvert/tree/master/bin/zztScreenshotter";
	bin        = path.join(progBasePath, "env/bin/python3");
	args       = r => [path.join(progBasePath, "zztScreenshotter.py"), r.inFile(), r.outDir()];
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	renameOut  = false;
}
