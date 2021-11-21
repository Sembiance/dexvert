import {Format} from "../../Format.js";
import {windowsSCR} from "../executable/windowsSCR.js";

export class aniST extends Format
{
	name           = "Ani ST";
	website        = "http://fileformats.archiveteam.org/wiki/AniST";
	ext            = [".scr", ".str"];
	mimeType       = "image/x-ani-st";
	converters     = [`abydosconvert[format:${this.mimeType}]`];
	forbiddenMagic = (new windowsSCR()).magic;
}
