import {Format} from "../../Format.js";

export class rayDreamDesignerScene extends Format
{
	name       = "Ray Dream Designer Scene";
	website    = "http://fileformats.archiveteam.org/wiki/COLLADA";
	ext        = [".rds", ".rd4", ".rd3"];
	safeExt    = ".rds";
	magic      = ["Ray Dream Designer scene", "Ray Dream Studio"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="RD4F" && macFileCreator==="RD4A";
	converters = ["rayDreamDesignerStudio55"];
}
