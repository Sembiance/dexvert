import {Format} from "../../Format.js";

export class picturePublisher extends Format
{
	name       = "Picture Publisher";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Publisher";
	ext        = [".pp5", ".pp4", ".ppf"];
	magic      = [/^Micrografx Picture Publisher [\d-]+ document/, "Micrografx Picture Publisher 5.0 :pp5:", /^x-fmt\/(85|176)( |$)/];
	converters = ["nconvert[format:pp5]", "nconvert[format:pp4]", "picturePublisher", "corelPhotoPaint"];
	verify     = ({meta}) => meta.colorCount>1;
}
