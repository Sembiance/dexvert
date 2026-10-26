import {Format} from "../../Format.js";

export class imperiumGalacticaAnimation extends Format
{
	name           = "Imperium Galactica Animation";
	ext            = [".ani"];
	forbidExtMatch = true;
	magic          = ["Imperium Galactica Animation", "Imperium Galactica Animation Video"];
	converters     = ["vibe2avi"];
}
