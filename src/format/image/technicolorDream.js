import {Format} from "../../Format.js";

export class technicolorDream extends Format
{
	name     = "Technicolor Dream";
	website  = "http://fileformats.archiveteam.org/wiki/Technicolor_Dream";
	ext      = [".lum", ".col"];
	auxFiles = (input, otherFiles) =>
	{
		// .lum can convert on it's own, but optionally uses a .col
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));
		return otherFile ? [otherFile] : false;
	};

	// Don't do anything with .col files
	untouched  = ({f}) => f.input.ext.toLowerCase()=== ".col";
	converters = ["recoil2png"];
}
