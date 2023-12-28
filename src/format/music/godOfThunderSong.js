import {Format} from "../../Format.js";

export class godOfThunderSong extends Format
{
	name       = "God of Thunder Song";
	website    = "https://vgmpf.com/Wiki/index.php?title=GOT";
	filename   = [/^song\d+$/i, /^(bosssong|opensong|winsong)$/i];
	converters = ["gamemus[format:got]"];
}
