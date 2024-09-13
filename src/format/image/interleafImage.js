import {Format} from "../../Format.js";

export class interleafImage extends Format
{
	name           = "Interleaf Image";
	website        = "http://fileformats.archiveteam.org/wiki/Interleaf_image";
	ext            = [".iimg", ".img"];
	forbidExtMatch = [".img"];
	magic          = ["Interleaf image", "Interleaf Image"];
	converters     = ["leaftoppm"];
}
