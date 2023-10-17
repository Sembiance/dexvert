import {Format} from "../../Format.js";

export class epocAIF extends Format
{
	name       = "EPOC Application Information File";
	website    = "http://fileformats.archiveteam.org/wiki/EPOC_AIF";
	ext        = [".aif"];
	magic      = ["EPOC/Symbian Application Info", "Psion Series 5 application information file"];
	converters = ["deark[module:epocimage]"];
}
