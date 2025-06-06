import {Format} from "../../Format.js";

export class xpk extends Format
{
	name       = "Amiga XPK Archive";
	website    = "http://fileformats.archiveteam.org/wiki/XPK";
	ext        = [".xpk"];
	magic      = ["Amiga xpkf.library compressed data", "XPK compressed data", "Archive: Amiga eXtended PacKer", "Archive: XPK container", /XPK-.{4}: /, "XPK-NUKE: ", "deark: xpk"];
	packed     = true;
	converters = ["ancient", "amigadepacker", "xfdDecrunch"];
}
