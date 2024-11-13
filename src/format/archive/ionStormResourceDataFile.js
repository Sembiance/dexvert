import {Format} from "../../Format.js";

export class ionStormResourceDataFile extends Format
{
	name           = "Ion Storm Resource Data File";
	website        = "http://fileformats.archiveteam.org/wiki/Image_Gallery_(Alchemy_Mindworks)";
	ext            = [".rdf"];
	forbidExtMatch = true;
	magic          = ["Ion Storm Resource Data File"];
	weakMagic      = true;
	converters     = ["foremost"];
}
