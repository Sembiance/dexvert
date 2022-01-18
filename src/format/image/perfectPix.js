import {Format} from "../../Format.js";

export class perfectPix extends Format
{
	name    = "Perfect Pix";
	website = "http://fileformats.archiveteam.org/wiki/Perfect_Pix";
	ext     = [".eve", ".odd", ".pph"];

	// All three files are required
	auxFiles = (input, otherFiles) =>
	{
		const requiredFiles = otherFiles.filter(otherFile => this.ext.filter(ext => ext!==input.ext.toLowerCase()).map(ext => input.name.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		return requiredFiles.length===2 ? requiredFiles : [];
	};

	// Don't do anything with .pal files
	untouched       = ({f}) => [".eve", ".odd"].includes(f.input.ext.toLowerCase());
	verifyUntouched = false;
	converters      = ["recoil2png"];
}
