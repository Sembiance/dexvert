import {Format} from "../../Format.js";

export class photoStudio extends Format
{
	name       = "PhotoStudio PSF";
	website    = "http://fileformats.archiveteam.org/wiki/PSF_(PhotoStudio)";
	ext        = [".psf"];
	magic      = ["photoStudio bitmap"];
	converters = ["nconvert", "imageAlchemy", "graphicWorkshopProfessional", "picturePublisher", "tomsViewer"];
}
