import {Format} from "../../Format.js";

export class macroMindProjector extends Format
{
	name        = "MacroMind Projector";
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="APPL" && macFileCreator==="MMPB";
	notes       = "This is an older Macromedia Projector file";
	unsupported = true;
}
