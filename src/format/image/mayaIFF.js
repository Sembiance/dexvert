import {Format} from "../../Format.js";

export class mayaIFF extends Format
{
	name           = "Alias Maya IFF Image";
	website        = "http://fileformats.archiveteam.org/wiki/Maya_IFF";
	ext            = [".iff", ".tdi"];
	forbidExtMatch = true;
	magic          = ["Alias Maya Image File", "Maya IFF bitmap", "Maya/TDI Explore :tdi:", /^fmt\/1169( |$)/];
	converters     = ["nconvert[format:tdi]"];
}
