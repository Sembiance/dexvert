import {Format} from "../../Format.js";

export class pmXV extends Format
{
	name           = "PM XV";
	website        = "http://fileformats.archiveteam.org/wiki/PM_(XV_image)";
	ext            = [".pm", ".pic"];
	forbidExtMatch = true;
	magic          = ["PM XV bitmap"];
	converters     = ["nconvert"];
	verify         = ({meta}) => meta.colorCount>1;
}
