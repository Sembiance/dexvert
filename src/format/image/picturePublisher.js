import {Format} from "../../Format.js";

export class picturePublisher extends Format
{
	name       = "Picture Publisher";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Publisher";
	ext        = [".pp5", ".pp4", ".ppf"];
	magic      = ["Micrografx Picture Publisher 5 document", /^x-fmt\/85( |$)/];
	notes      = "Couldn't actually get any of my sample files to convert.";
	converters = ["nconvert", "picturePublisher", "corelPhotoPaint"];
}
