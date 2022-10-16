import {Format} from "../../Format.js";

export class adobeIllustrator extends Format
{
	name       = "Adobe Illustrator";
	website    = "http://fileformats.archiveteam.org/wiki/Adobe_Illustrator_Artwork";
	ext        = [".ai"];
	magic      = ["Adobe Illustrator graphics", /^fmt\/(418|420|422)( |$)/];
	weakMagic  = true;
	converters = ["adobeIllustrator", "corelPhotoPaint", "picturePublisher", "hiJaakExpress", "corelDRAW"];
	verify     = ({meta}) => meta.colorCount>1;
}
