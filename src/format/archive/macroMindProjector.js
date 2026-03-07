import {Format} from "../../Format.js";

export class macroMindProjector extends Format
{
	name       = "MacroMind Projector/Director";
	idMeta     = ({macFileType, macFileCreator}) => (
		(macFileType==="APPL" && macFileCreator==="MMPB") ||
		macFileType==="VWMD" ||	// used to restrict this to macFileCreator==="MMDR" but some files in the wild don't have a creator, Garelly1624
		(["VWZP", "VWSC"].includes(macFileType) && macFileCreator==="MMVW"));
	auxFiles   = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);
	converters = ["unmacromind"];
}
