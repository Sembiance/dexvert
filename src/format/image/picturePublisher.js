import {Format} from "../../Format.js";

export class picturePublisher extends Format
{
	name       = "Picture Publisher";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Publisher";
	ext        = [".pp5", ".pp4"];
	magic      = ["Micrografx Picture Publisher 5 document"];
	notes      = "Couldn't actually get any of my sample files to convert.";
	converters = ["nconvert", "corelPhotoPaint"];
}
