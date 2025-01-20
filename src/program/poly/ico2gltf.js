import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("ico2gltf");

export class ico2gltf extends Program
{
	website    = "https://github.com/MightyDuke/ico2gltf";
	bin        = path.join(progBasePath, "env/bin/python3");
	args       = async r => [path.join(progBasePath, "ico2gltf.py"), "-o", await r.outFile("out.glb"), r.f.aux.absolute];
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	renameOut  = true;
}
