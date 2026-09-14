import {Format} from "../../Format.js";

export class ignitionPIC extends Format
{
	name           = "Ignition PIC Image";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = [/^geViewer: PIC_Ignition( |$)/];
	converters     = ["gameextractor[renameOut][codes:PIC_Ignition]"];
}
