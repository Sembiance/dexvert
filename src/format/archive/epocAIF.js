import {Format} from "../../Format.js";

export class epocAIF extends Format
{
	name       = "EPOC Application Information File";
	website    = "http://fileformats.archiveteam.org/wiki/EPOC_AIF";
	ext        = [".aif"];
	magic      = ["EPOC/Symbian Application Info", "Psion Series 5 application information file", "deark: epocimage (EPOC AIF)"];
	converters = ["deark[module:epocimage]"];
}
