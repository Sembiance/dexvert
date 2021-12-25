import {Format} from "../../Format.js";

export class xpk extends Format
{
	name       = "Amiga XPK Archive";
	website    = "http://fileformats.archiveteam.org/wiki/XPK";
	ext        = [".xpk"];
	magic      = ["Amiga xpkf.library compressed data", "XPK compressed data", "XPK-SQSH: ", "XPK-NUKE: "];
	converters = ["amigadepacker", "ancient", "xfdDecrunch"];
}
