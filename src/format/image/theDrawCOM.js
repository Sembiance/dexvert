import {Format} from "../../Format.js";

export class theDrawCOM extends Format
{
	name           = "TheDraw .COM File";
	website        = "http://fileformats.archiveteam.org/wiki/TheDraw_COM_File";
	ext            = [".com"];
	forbidExtMatch = true;
	mimeType       = "image/x-thedraw";
	magic          = ["TheDraw COM file screen save"];
	converters     = ["dosEXEScreenshot"];
}
