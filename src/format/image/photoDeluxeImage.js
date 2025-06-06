import {xu} from "xu";
import {Format} from "../../Format.js";

export class photoDeluxeImage extends Format
{
	name           = "PhotoDeluxe Image";
	website        = "http://fileformats.archiveteam.org/wiki/PhotoDeluxe";
	ext            = [".pdd"];
	forbidExtMatch = true;
	magic          = ["Adobe Photoshop Elements (PhotoDeluxe) image", /^Adobe Photoshop Image \(PhotoDeluxe\)/, "Adobe Photoshop Document :pdd:"];
	metaProvider   = ["image"];
	converters     = ["gimp", "iio2png", "convert"];
}
