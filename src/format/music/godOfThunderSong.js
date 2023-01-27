import {Format} from "../../Format.js";

export class godOfThunderSong extends Format
{
	name       = "God of Thunder Song";
	website    = "https://moddingwiki.shikadi.net/wiki/God_of_Thunder_Music_Format";
	filename   = [/^song\d+$/i, /^bosssong|opensong|winsong$/i];
	converters = ["gamemus[format:got]"];
}
