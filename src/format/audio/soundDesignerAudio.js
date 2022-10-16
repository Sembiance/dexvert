import {xu} from "xu";
import {Format} from "../../Format.js";

export class soundDesignerAudio extends Format
{
	name           = "Sound Designer Audio";
	ext            = [".dig", ".sd"];
	forbidExtMatch = true;
	magic          = ["Sound Designer audio"];
	converters     = ["awaveStudio"];
}
