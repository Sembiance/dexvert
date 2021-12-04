import {Format} from "../../Format.js";

export class amstradMode5 extends Format
{
	name = "Amstrad CPC Mode 5 Image";
	ext  = [".cm5", ".gfx"];

	// Both .cm5 and .gfx are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));

	// Don't do anything with .gfx files
	untouched = ({f}) => f.input.ext.toLowerCase()===".pal";

	converters = ["recoil2png"];
}
