import {Format} from "../../Format.js";

export class rar extends Format
{
	name         = "Roshal Archive";
	website      = "http://fileformats.archiveteam.org/wiki/RAR";
	ext          = [".rar"];
	magic        = ["RAR archive data", "RAR compressed archive", "RAR Archive"];
	converters   = ["unrar", "UniExtract"];
	metaProvider = ["unrarMeta"];
	untouched    = dexState => !!dexState.meta.passwordProtected;
	post         = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="unrar")?.meta || {});
}

