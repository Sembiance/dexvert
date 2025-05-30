import {Format} from "../../Format.js";

export class panasonicRaw extends Format
{
	name           = "Panasonic RAW";
	website        = "http://fileformats.archiveteam.org/wiki/Panasonic_RAW/RW2";
	ext            = [".rw2", ".raw", ".rwl"];
	forbidExtMatch = [".raw"];
	magic          = ["Panasonic RAW image", "Panasonic Raw", "Leica RAW image", "image/x-panasonic-rw2", "deark: tiff (Panasonic RAW/RW2)", /^fmt\/662( |$)/];
	mimeType       = "image/x-panasonic-raw";
	metaProvider   = ["image", "darkTable"];
	converters     = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
