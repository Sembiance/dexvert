import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("activemime-format");

export class activeMimeExtractor extends Program
{
	website    = "https://github.com/idiom/activemime-format";
	package    = "dev-lang/python:2.7";
	bin        = path.join(progBasePath, "env/bin/python");
	unsafe     = true;
	args       = r => [path.join(progBasePath, "amime.py"), `--extract=${r.outDir({absolute : true})}`, r.inFile({absolute : true})];
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	renameOut  = false;
}
