import {Format} from "../../Format.js";

export class koepacAudioArchive extends Format
{
	name           = "Koepac audio archive";
	ext            = [".koe"];
	forbidExtMatch = true;
	magic          = ["Koepac audio archive"];
	converters     = ["vibe2wav"];
}
