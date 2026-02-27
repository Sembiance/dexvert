import {Format} from "../../Format.js";

export class ghostbustersSanctumOfSlimeArchive extends Format
{
	name           = "Ghostbusters Sanctum of Slime Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["dragon: tonga "];
	converters     = ["dragonUnpacker[types:tonga]"];
}
