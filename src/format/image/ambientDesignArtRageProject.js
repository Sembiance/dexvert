import {Format} from "../../Format.js";

export class ambientDesignArtRageProject extends Format
{
	name           = "Ambient Design ArtRage project";
	ext            = [".ptg"];
	forbidExtMatch = true;
	magic          = ["Ambient Design ArtRage project", "Artrage :ptg:"];
	converters     = ["nconvert[format:ptg]"];
	notes          = "nconvert really just extracts a thumbnail, but better than nothing for now.";
}
