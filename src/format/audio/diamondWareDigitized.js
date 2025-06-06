import {Format} from "../../Format.js";

export class diamondWareDigitized extends Format
{
	name           = "DiamondWare Digitized Audio";
	website        = "http://fileformats.archiveteam.org/wiki/DiamondWare_Digitized";
	ext            = [".dwd"];
	forbidExtMatch = true;
	magic          = ["DiamondWare Digitized audio", "DWD (DiamondWare Digitized) (dwd)"];
	converters     = ["ffmpeg[libre][format:dwd][outType:mp3]", "awaveStudio"];
}
