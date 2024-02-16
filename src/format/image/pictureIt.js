import {Format} from "../../Format.js";

const _PICTUREIT_MAGIC = ["Microsoft Picture It!", /^fmt\/936( |$)/];
export {_PICTUREIT_MAGIC};

export class pictureIt extends Format
{
	name           = "Picture It!";
	website        = "http://fileformats.archiveteam.org/wiki/MIX_(Picture_It!)";
	ext            = [".mix"];
	forbidExtMatch = true;
	magic          = _PICTUREIT_MAGIC;
	converters     = ["photoDraw", "deark[module:cfb]", "nconvert"];
	notes          = "Only thumbnail extraction is supported.";
}
