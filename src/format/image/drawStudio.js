import {Format} from "../../Format.js";

export class drawStudio extends Format
{
	name        = "DrawStudio Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/DrawStudio";
	ext         = [".dsdr"];
	magic       = ["DrawStudio Drawing"];
	unsupported = true;
	notes       = "Amiga program DrawStudio creates these. No known converter. DrawStudio demo available: https://aminet.net/package/gfx/edit/DrawStudioFPU";
}
