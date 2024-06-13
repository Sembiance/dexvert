import {Format} from "../../Format.js";

export class glPaintPIC extends Format
{
	name           = "GLPaint PIC";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = ["GLPaint PIC"];
	converters     = ["graphicWorkshopProfessional"];
}
