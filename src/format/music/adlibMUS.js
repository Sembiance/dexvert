import {Format} from "../../Format.js";

export class adlibMUS extends Format
{
	name           = "AdLib MUS";
	website        = "https://vgmpf.com/Wiki/index.php?title=MUS_(AdLib)";
	ext            = [".mus"];
	forbidExtMatch = true;
	magic          = ["AdLib MUS"];
	converters     = ["adplay", "gamemus"];	// gamemus will only really handle a tiny tiny subset
}
