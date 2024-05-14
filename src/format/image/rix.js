import {Format} from "../../Format.js";

export class rix extends Format
{
	name       = "ColoRIX";
	website    = "http://fileformats.archiveteam.org/wiki/ColoRIX";
	ext        = [".rix", ".sca", ".scb", ".scc", ".sce", ".scf", ".scg", ".sci", ".sck", ".scl", ".scn", ".sco", ".scp", ".scq", ".scr", ".sct", ".scu", ".scv", ".scw", ".scx", ".scy", ".scz"];
	weakExt    = [".scr", ".sxr"];
	magic      = ["ColoRIX bitmap", "ColoRIX Image"];
	idMeta     = ({macFileType}) => macFileType==="RIX3";
	converters = ["nconvert", "deark[module:colorix]", "pv[matchType:magic]"];
}
