import {Format} from "../../Format.js";

export class psionDatabase extends Format
{
	name           = "Psion Database";
	ext            = [".dbf", ".odb"];
	forbidExtMatch = true;
	magic          = ["Psion serie 3 Database"];
	converters     = ["strings"];
}
