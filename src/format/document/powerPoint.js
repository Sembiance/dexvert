import {Format} from "../../Format.js";

export class powerPoint extends Format
{
	name           = "Power Point";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_PowerPoint";
	ext            = [".ppt", ".pp", ".ppsx", ".pptm", ".pptx", ".potx"];
	forbidExtMatch = true;
	magic          = [
		"Microsoft PowerPoint", "PowerPoint Microsoft Office Open XML Format document", "Forethought PowerPoint", "PowerPoint Presentation", /^PowerPoint :(ppt|pps):/,
		/^fmt\/(125|126|215|629|631|1747|1748|1866|1867)( |$)/, /^x-fmt\/88( |$)/
	];
	idMeta         = ({macFileType, macFileCreator}) => ["PPSS", "SLD3", "SLD8", "SLDS", "PPOT"].includes(macFileType) && ["PPNT", "PPT3"].includes(macFileCreator);
	converters     = ["soffice[format:PowerPoint3]", "soffice[format:MS PowerPoint 97]"];
}
