import {Format} from "../../Format.js";

export class rayDreamDesignerScene extends Format
{
	name       = "Ray Dream Designer Scene";
	website    = "http://fileformats.archiveteam.org/wiki/COLLADA";
	ext        = [".rds", ".rd4", ".rd3"];
	safeExt    = ".rds";
	magic      = ["Ray Dream Designer scene", "Ray Dream Studio"];
	idMeta     = ({macFileType, macFileCreator}) => ["RD3F", "RD4F", "RDSF"].includes(macFileType) && ["RD3A", "RD4A", "RD5A"].includes(macFileCreator);
	converters = ["rayDreamDesignerStudio55"];
}
