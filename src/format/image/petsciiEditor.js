import {Format} from "../../Format.js";

export class petsciiEditor extends Format
{
	name = "PETSCII Editor";
	ext  = [".scr", ".col"];

	// Both .scr and .col are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));

	// Don't do anything with .col files
	untouched = ({f}) => f.input.ext.toLowerCase()===".col";

	converters = ["recoil2png"];
}
