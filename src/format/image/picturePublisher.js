import {Format} from "../../Format.js";

export class picturePublisher extends Format
{
	name       = "Picture Publisher";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Publisher";
	ext        = [".pp5", ".pp4", ".ppf"];
	magic      = [/^Micrografx Picture Publisher [\d-]+ document/, /^x-fmt\/(85|176)( |$)/];
	converters = ["nconvert", "picturePublisher", "corelPhotoPaint"];
	verify     = ({meta}) => meta.colorCount>1;
}
