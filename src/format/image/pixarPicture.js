import {Format} from "../../Format.js";

export class pixarPicture extends Format
{
	name           = "Pixar Picture";
	website        = "http://fileformats.archiveteam.org/wiki/Pixar_picture";
	ext            = [".pxr", ".pixar", ".pic", ".picio"];
	forbidExtMatch = true;
	magic          = ["Pixar picture bitmap", /^Pixar picture .*:pxr:$/];
	converters     = ["imconv[format:pic]", "nconvert[format:pxr]"];
}
