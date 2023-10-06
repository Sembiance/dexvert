import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("zztScreenshotter");

export class zztScreenshotter extends Program
{
	website    = "https://github.com/Sembiance/dexvert/tree/master/bin/zztScreenshotter";
	package    = "dev-lang/python:3.8";
	bin        = path.join(progBasePath, "env/bin/python3.8");
	unsafe     = true;
	args       = r => [path.join(progBasePath, "zztScreenshotter.py"), r.inFile(), r.outDir()];
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	notes      = "If this fails to run due to missing libtiff, run as root: cd /usr/lib64 && ln -s libtiff.so.6.0.2 libtiff.so.5";
	renameOut  = false;
}
