import {xu} from "xu";
import {Format} from "../../Format.js";

export class completeAnimatorFilm extends Format
{
	name           = "The Complete Animator Film";
	ext            = [".tca"];
	forbidExtMatch = true;
	magic          = ["The Complete Animator Film video"];
	converters     = ["nihav"];
}
