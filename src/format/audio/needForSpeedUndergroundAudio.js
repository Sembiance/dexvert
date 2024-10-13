import {Format} from "../../Format.js";

export class needForSpeedUndergroundAudio extends Format
{
	name           = "Need for Speed: Underground audio";
	ext            = [".abk"];
	forbidExtMatch = true;
	magic          = ["Need for Speed: Underground audio"];
	converters     = ["vgmstream"];
}
