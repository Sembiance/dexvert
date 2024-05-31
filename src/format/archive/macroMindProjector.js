import {Format} from "../../Format.js";

export class macroMindProjector extends Format
{
	name        = "MacroMind Projector/Director";
	idMeta      = ({macFileType, macFileCreator}) => ((macFileType==="APPL" && macFileCreator==="MMPB") || (macFileType==="VWMD" && macFileCreator==="MMDR"));
	notes       = "This is an older Macromedia Projector file, Macintosh version";
	unsupported = true;
}
