import {Format} from "../../Format.js";

export class elecbyteMUGENFont extends Format
{
	name           = "Elecbyte M.U.G.E.N. font";
	website        = "http://fileformats.archiveteam.org/wiki/FIGlet_font";
	ext            = [".fnt"];
	forbidExtMatch = true;
	magic          = ["Elecbyte M.U.G.E.N. font"];
	converters     = ["wuimg[format:eb_fnt]"];
}
