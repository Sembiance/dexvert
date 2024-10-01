import {Format} from "../../Format.js";

export class brenderPIX extends Format
{
	name       = "BRender PIX";
	website    = "http://fileformats.archiveteam.org/wiki/BRender_PIX";
	ext        = [".pix"];
	weakExt    = true;
	magic      = ["BRender PIX bitmap", "BRender PIX image (brender_pix)"];
	converters = ["ffmpeg[outType:png]"];
}
