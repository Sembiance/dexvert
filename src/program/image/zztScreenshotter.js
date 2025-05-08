import {Program} from "../../Program.js";

export class zztScreenshotter extends Program
{
	website   = "https://github.com/Sembiance/dexvert/tree/master/bin/zztScreenshotter";
	package   = "dev-python/zookeeper";
	bin       = "python3";
	unsafe    = true;
	args      = r => [Program.binPath("zztScreenshotter.py"), r.inFile(), r.outDir()];
	renameOut = false;
}
