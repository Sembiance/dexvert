import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class uhs2html extends Program
{
	website   = "http://www.emulinks.de/software.html";
	package   = "games-util/uhs2html";
	unsafe    = true;
	bin       = "uhs2html";
	args      = r => [r.inFile(), "dexout"];
	postExec  = async r => await fileUtil.moveAll(path.join(r.outDir({absolute : true}), "dexout"), path.join(r.outDir({absolute : true})), {unlinkSrc : true});
	cwd       = r => r.outDir();
	renameOut = false;
}
