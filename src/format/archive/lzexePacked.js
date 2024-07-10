import {Format} from "../../Format.js";
import {_GIFEXE_MAGIC} from "../image/gifexe.js#test";

export class lzexePacked extends Format
{
	name           = "LZEXE Packed";
	website        = "http://fileformats.archiveteam.org/wiki/LZEXE";
	magic          = ["Packer: LZEXE", "LZEXE compressed DOS executable"];
	forbiddenMagic = _GIFEXE_MAGIC;
	packed         = true;
	converters     = ["deark[module:lzexe]"];
}
