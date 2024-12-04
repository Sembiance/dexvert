import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("pywebarchive");

export class pywebarchive extends Program
{
	website    = "https://pypi.org/project/pywebarchive/";
	bin        = path.join(progBasePath, "env/bin/python3");
	args       = async r => [path.join(progBasePath, "extractor.py"), r.inFile(), await r.outFile("webarchive.html")];
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	postExec   = async r => await Deno.rename(path.join(r.f.outDir.absolute, "webarchive.html"), path.join(r.f.outDir.absolute, `${r.originalInput.base}.html`));
	renameOut  = false;
}
