import {Format} from "../../Format.js";

export class bioWareMusicUnit extends Format
{
	name           = "BioWare Music Unit";
	ext            = [".bmu"];
	forbidExtMatch = true;
	magic          = ["Aurora Engine BioWare Music Unit"];
	converters     = ["dd[bs:8][skip:1] -> ffmpeg[outType:mp3]"];
}
