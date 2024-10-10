import {Format} from "../../Format.js";

export class flankerSoundLibrary extends Format
{
	name           = "Flanker Sound Library";
	ext            = [".sfx"];
	forbidExtMatch = true;
	magic          = ["Sound library / container"];
	converters     = ["foremost -> sox"];
}
