import {Format} from "../../Format.js";

export class spacemaker extends Format
{
	name           = "Spacemaker";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = ["16bit DOS COM Spacemaker compressed", "deark: spacemaker"];
	packed         = true;
	converters     = ["deark[module:spacemaker]"];
}
