import {Format} from "../../Format.js";

export class adobeIllustrator extends Format
{
	name       = "Adobe Illustrator";
	website    = "http://fileformats.archiveteam.org/wiki/Adobe_Illustrator_Artwork";
	ext        = [".ai"];
	magic      = ["Adobe Illustrator graphics", /^fmt\/422( |$)/];
	priority   = this.PRIORITY.LOW;	// Allow EPS to get it first
	converters = ["adobeIllustrator", "corelPhotoPaint", "picturePublisher", "hiJaakExpress", "corelDRAW"];
}
