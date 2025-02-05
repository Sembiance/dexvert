import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("gameViewerLinux");

export class gameViewerLinux extends Program
{
	website    = "https://game-viewer.org/plugins.php";
	bin        = path.join(progBasePath, "env/bin/python3");
	flags      = {
		plugin : "Which plugin to use (don't include the g_ or .py suffix). REQUIRED"
	};
	args       = r => [path.join(progBasePath, "gameViewerExtract.py"), r.flags.plugin, r.inFile({absolute : true}), r.outDir({absolute : true})];
	runOptions = {cwd : progBasePath, env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	renameOut  = true;
}
