import {Format} from "../../Format.js";

export class animationMagicAnimation extends Format
{
	name           = "Animation Magic video/Animation";
	ext            = [".ani"];
	forbidExtMatch = true;
	magic          = ["Animation Magic video/Animation"];
	converters     = ["vibe2avi"];
}
