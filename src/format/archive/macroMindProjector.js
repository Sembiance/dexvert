import {Format} from "../../Format.js";

export class macroMindProjector extends Format
{
	name       = "MacroMind Projector/Director";
	idMeta     = ({macFileType, macFileCreator}) => ((macFileType==="APPL" && macFileCreator==="MMPB") || (macFileType==="VWMD" && macFileCreator==="MMDR"));
	auxFiles   = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);
	converters = ["unmacromind"];
}
