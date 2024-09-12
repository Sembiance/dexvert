import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class archmage extends Program
{
	website    = "https://github.com/dottedmag/archmage";
	package    = "app-text/archmage";
	notes      = "Right now we just extract all the files, raw. archmage says it can convert to better HTML or PDF but it's got bugs and that doesn't work.";
	bin        = "archmage";
	args       = async r => ["-x", r.inFile(), await r.outFile("dexout")];
	postExec   = async r => await fileUtil.moveAll(path.join(r.f.root, r.args.at(-1)), path.join(r.outDir({absolute : true})), {unlinkSrc : true});
	skipVerify = true;
	renameOut  = false;
}
