import {Format} from "../../Format.js";

export class riffRDIB extends Format
{
	name           = "RIFF RDIB";
	website        = "http://fileformats.archiveteam.org/wiki/RDIB";
	ext            = [".rdi", ".rib", ".dib"];
	forbidExtMatch = [".dib"];
	magic          = ["RIFF Device Independent Bitmap", /^RIFF .*data, device-independent bitmap/];
	converters     = ["deark[module:riff]"];
}
