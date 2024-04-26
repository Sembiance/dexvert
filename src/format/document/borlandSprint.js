import {Format} from "../../Format.js";

export class borlandSprint extends Format
{
	name        = "Borland Sprint";
	website     = "https://winworldpc.com/product/borland-sprint";
	ext         = [".spr"];
	unsupported = true;
	converters  = ["softwareBridge[format:borlandSprint]"];
	notes       = "DOS based word processor. Haven't investigated it for magic. Not 100% sure my sample file is Borland Sprint, but couldn't find another WordProcessor called sprint.";
}
