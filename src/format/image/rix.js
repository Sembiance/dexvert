import {Format} from "../../Format.js";

const _WEAK_EXT = [".sca", ".scb", ".scc", ".sce", ".scf", ".scg", ".sci", ".sck", ".scl", ".scn", ".sco", ".scp", ".scq", ".scr", ".sct", ".scu", ".scv", ".scw", ".scx", ".scy", ".scz"];

export class rix extends Format
{
	name           = "ColoRIX";
	website        = "http://fileformats.archiveteam.org/wiki/ColoRIX";
	ext            = [".rix", ..._WEAK_EXT];
	forbidExtMatch = _WEAK_EXT;
	magic          = ["ColoRIX bitmap", "ColoRIX Image", "deark: colorix", "ColoRIX :rix:"];
	idMeta         = ({macFileType}) => macFileType==="RIX3";
	converters     = ["nconvert[format:rix]", "deark[module:colorix]", "pv[matchType:magic]"];
}
