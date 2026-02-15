import {Format} from "../../Format.js";

export class mur extends Format
{
	name    = "C.O.L.R. Object Editor";
	website = "http://fileformats.archiveteam.org/wiki/C.O.L.R._Object_Editor";
	ext     = [".mur", ".pal"];

	// Both .mur and .pal are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));

	// Don't do anything with .pal files
	untouched       = ({f}) => f.input.ext.toLowerCase()===".pal";
	verifyUntouched = false;
	converters      = ["recoil2png[format:MUR]"];
}
