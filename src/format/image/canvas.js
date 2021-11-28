import {Format} from "../../Format.js";

export class canvas extends Format
{
	name = "Atari Canvas";
	ext  = [".cpt", ".hbl", ".ful"];
	
	auxFiles = (input, otherFiles) =>
	{
		// .ful is standalone
		if(input.ext.toLowerCase()===".ful")
			return false;
		
		// .hbl is useless without a .cpt, but .hbl doesn't convert into anything, it's extra info
		if(input.ext.toLowerCase()===".hbl")
			return otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.cpt`);
		
		// .cpt can convert on it's own, but optionally uses an .hbl
		const hblFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.hbl`);
		return hblFile ? [hblFile] : false;
	};

	// Don't do anything with .hbl files
	untouched = ({f}) => f.input.ext.toLowerCase()===".hbl"

	converters = ["recoil2png"]
}
