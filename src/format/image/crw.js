import {Format} from "../../Format.js";

export class crw extends Format
{
	name         = "Canon Image File Format";
	website      = "http://fileformats.archiveteam.org/wiki/Camera_Image_File_Format";
	ext          = [".crw"];
	magic        = ["Canon CIFF raw image data", "Canon RAW format", "image/x-canon-crw", /^fmt\/593( |$)/];
	mimeType     = "image/x-canon-crw";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
