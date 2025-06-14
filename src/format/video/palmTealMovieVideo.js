import {xu} from "xu";
import {Format} from "../../Format.js";

export class palmTealMovieVideo extends Format
{
	name           = "Palm TealMovie Video";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["Palm TealMovie"];
	converters     = ["nihav"];
}
