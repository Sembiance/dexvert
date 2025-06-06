import {Format} from "../../Format.js";

export class hemeraThumbnailsArchive extends Format
{
	name       = "Hemera Thumbnails Archive";
	website    = "http://fileformats.archiveteam.org/wiki/HTA_(Hemera)";
	ext        = [".hta"];
	magic      = ["Hemera Thumbnails Archive", "deark: hta", "Hemera Thumbs :hta:"];
	converters = ["deark[module:hta]", "nconvert[format:hta][extractAll]"];
}
