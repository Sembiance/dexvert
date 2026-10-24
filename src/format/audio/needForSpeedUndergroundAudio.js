import {Format} from "../../Format.js";

export class needForSpeedUndergroundAudio extends Format
{
	name           = "Need for Speed: Underground audio";
	ext            = [".abk"];
	forbidExtMatch = true;
	magic          = ["Need for Speed: Underground audio", "EA Black Box Audio Bank container", "vgmstream: ea_abk_schl"];
	converters     = ["vgmstream[types:ea_abk_schl]"];
}
