import {Format} from "../../Format.js";

export class alchemyMindworksGallery extends Format
{
	name       = "Alchemy Mindworks Image Gallery";
	website    = "http://fileformats.archiveteam.org/wiki/Image_Gallery_(Alchemy_Mindworks)";
	ext        = [".gal"];
	magic      = ["Alchemy Mindworks Image Gallery", "deark: imggal_alch"];
	converters = ["deark[module:imggal_alch]"];
}
