import {Format} from "../../Format.js";

export class orgPlus extends Format
{
	name           = "OrgPlus";
	website        = "http://fileformats.archiveteam.org/wiki/OrgPlus";
	ext            = [".opx", ".ops"];
	forbidExtMatch = true;
	magic          = ["OrgPlus Organization Chart", /^fmt\/1457( |$)/];
	converters     = ["strings"];
}
