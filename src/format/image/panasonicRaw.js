import {Format} from "../../Format.js";

export class panasonicRaw extends Format
{
	name           = "Panasonic RAW";
	website        = "http://fileformats.archiveteam.org/wiki/Panasonic_RAW";
	ext            = [".rw2", ".raw", ".rwl"];
	forbidExtMatch = [".raw"];
	magic          = ["Panasonic RAW image", "Panasonic Raw", "Leica RAW image"];
	mimeType       = "image/x-panasonic-raw";
	metaProvider   = ["image", "darkTable"];
	converters     = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
