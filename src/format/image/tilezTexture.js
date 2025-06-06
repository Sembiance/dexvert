import {Format} from "../../Format.js";

export class tilezTexture extends Format
{
	name           = "Tilez texture";
	website        = "http://fileformats.archiveteam.org/wiki/Tilez_texture";
	ext            = [".til"];
	forbidExtMatch = true;
	magic          = ["Tilez texture", "Buttonz & Tilez texture :til:"];
	converters     = ["nconvert[format:til]"];
}
