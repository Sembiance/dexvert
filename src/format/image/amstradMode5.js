import {Format} from "../../Format.js";

export class amstradMode5 extends Format
{
	name            = "Amstrad CPC Mode 5 Image";
	ext             = [".cm5", ".gfx"];
	auxFiles        = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));	// Both .cm5 and .gfx are required
	untouched       = ({f}) => f.input.ext.toLowerCase()===".gfx";	// Don't do anything with .gfx files
	verifyUntouched = false;
	converters      = ["recoil2png[format:CM5]"];
}
