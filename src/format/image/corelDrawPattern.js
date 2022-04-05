import {Format} from "../../Format.js";

export class corelDrawPattern extends Format
{
	name           = "Corel Draw Pattern";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = [/Corel Draw Pattern/];
	notes          = "Only the preview image is supported at the moment.";
	converters     = ["deark"];
}
